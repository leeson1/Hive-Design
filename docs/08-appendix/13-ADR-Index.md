# 13 ADR Index

## Purpose

- 把 MVP 仍需明确的实现选择沉淀为可追溯的 ADR。
- 避免关键决策继续只停留在讨论语气。
- 为首个实现仓提供稳定的实现前提。

## Scope

- 本文只记录当前已收敛的 MVP 决策。
- 后续若决策变化，应新增或 supersede 对应 ADR，而不是静默改文。

## ADR-0001：MVP 使用 SQLite + Filesystem

### Context

- Hive MVP 已限定为单仓库、单 active plan、单 writer。
- 需要一个能稳定承载 authoritative state、change-set、outbox、event log、checkpoint 的最小后端组合。
- 当前主要风险在控制平面闭环，而不在分布式吞吐。

### Decision

- MVP 采用 `SQLite + filesystem`。
- SQLite 承载结构化对象、change-set、outbox、event log、checkpoint、migration state。
- filesystem 承载 artifacts、logs、workspaces。

### Consequences

- 首版不依赖 Postgres、MQ、object storage。
- 本地调试、回放、fixture 执行成本更低。
- 后续升级时必须保持 change-set / outbox / checkpoint 语义不变。

## ADR-0002：MVP 首适配器选 Codex

### Context

- 首版必须在 Claude Code 与 Codex 中选择 first adapter。
- capability matrix 显示 Codex 在 workspace isolation、artifact collection、log collection 上当前文档化边界更适合 MVP。
- restore、soft cancel、heartbeat 两边都还不能作为硬依赖。

### Decision

- `Codex` 作为 `Primary First Adapter`。
- `Claude Code` 作为 `Secondary Later Adapter`。

### Consequences

- 首版实现优先做 `codex` adapter。
- 仍必须保留 host-side monitor、recovery、acceptance、lock enforcement。
- Claude Code 的适配进入第二阶段验证与落地。

## ADR-0003：MVP 先做 Single Writer

### Context

- authoritative object state、change-set、outbox、event log 需要稳定提交序列。
- 多 writer 会立刻引入 leader election、锁竞争、消息一致性和重复派发复杂度。
- 当前 MVP 目标是先验证闭环，不是先做横向扩展。

### Decision

- MVP 只允许一个 control-plane writer 提交 authoritative state。
- 所有写命令通过 single writer gate 串行提交。

### Consequences

- 首版默认单进程 runtime。
- API / callback / runtime jobs 都必须通过统一 writer path。
- 多 writer 扩展被明确延后到 MVP 闭环稳定之后。

## ADR-0004：Live Restore 不是硬依赖

### Context

- 当前 executor validation plan 尚未证明 run-level restore fidelity。
- 若把 live restore 当硬依赖，会把 recovery 绑死在执行器私有能力上。
- Hive 的设计原则要求 continuity 来自外部状态，而不是会话连续性魔法。

### Decision

- MVP 恢复路径默认采用 `rehydrate + reassign`。
- `restore_run(...)` 仅允许作为 best-effort 可选能力。

### Consequences

- 恢复协议必须能在没有 live restore 的前提下成立。
- adapter 不得把 session continuity 伪装成原 run 恢复。
- validation 通过前，restore 能力不能升级为调度层硬依赖。

## ADR-0005：MVP 先做 Path Lock，而不是完整 Lock Federation

### Context

- 当前最直接的并发风险来自同仓路径写冲突。
- repo federation、跨仓锁协调会显著增加控制面和调度面的复杂度。
- 现有文档已允许 repo / module / path 三层语义，但 MVP 只需要证明最小冲突控制有效。

### Decision

- MVP 默认只实现 `path lock`。
- `module` 与 `repo` lock 先保留 schema 与语义，不作为首版必做能力。

### Consequences

- 首版冲突检测围绕 `allowed_paths`、`forbidden_paths`、`path_locks` 展开。
- stale lock recovery、duplicate dispatch prevention 先围绕 path 级场景验证。
- 完整 lock federation 被明确延后。

## ADR-0006：Checkpoint 是派生快照，不是事实源

### Context

- Hive 已明确 authoritative state 是当前事实来源，event log 是历史与重放输入。
- 若 checkpoint 被当事实源，会在恢复时反向污染对象状态。
- MVP 需要恢复快照，但不能牺牲事实层级。

### Decision

- checkpoint 只作为 derived snapshot。
- 恢复时以 authoritative object state 为准，checkpoint 只提供 cursor 与 open object summary。

### Consequences

- checkpoint writer 不得覆盖对象事实。
- recovery reconciliation 必须先读 object state，再对照 checkpoint。
- checkpoint 可以导出为文件，但导出文件不是当前事实。

## ADR-0007：Compiled Artifact 必须采用 Metadata Row + Payload Root

### Context

- vNext 需要把 `Evidence Pack / Product Spec / Task Graph / Run Contract / Session Scaffold` durable 化。
- 仅有协议层 schema 还不足以实现 freshness、pointer switch、supersession 与审计。
- 若只写 payload 文件，无法稳定索引与事务化切换 active pointer。

### Decision

- compiled artifact 一律采用 `metadata row + payload root` 分离模型。
- metadata row 存 SQLite，payload 存 filesystem。
- artifact 引用统一采用 `artifact://<artifact_type>/<artifact_id>[#entry]`。

### Consequences

- active pointer 可以稳定指向 artifact，而不需要把正文嵌进 runtime object。
- payload durable、pointer switch、supersession 可以拆成显式 change-set。
- dossier、scaffold、artifact 仍保持 derived state 身份。

## ADR-0008：Compilation Activation 必须晚于 Payload Durable

### Context

- compilation batch 与 runtime pointer 更新都属于 single-writer 控制面写路径。
- payload 在 filesystem，pointer 在 SQLite，天然不共享单事务。
- 若先切 pointer 再落 payload，会产生悬空 active ref。

### Decision

- 编译必须拆成 `prepare` 与 `activate` 两个边界。
- 只有在 payload durable 后，才允许 activate change-set 切换 pointer。
- supersession mapping 与 pointer switch 必须在同一 activate change-set 内完成。

### Consequences

- 实现层需要显式处理 `compiled_pending_activation` 状态。
- recovery 可以重试 activation，而不是误把半成品当 canonical output。
- compile failure / partial compile 不会污染 active runtime 引用。

## Acceptance Criteria

- 读者能明确看到每个关键实现选择的 context、decision、consequences。
- MVP 的 storage、executor、single writer、live restore、path lock、checkpoint、artifact durable 边界取舍已不再悬空。
- 后续若变化，可以在此基础上继续演进而不是重新口头讨论。
