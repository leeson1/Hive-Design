# 13 vNext 最小实现切片与阶段计划

## Purpose

- 把 vNext 从“协议已收敛”收口为“第一批必须落地的实现切片”。
- 明确首批必须落地的对象、命令、测试门和验收标准。
- 防止实现阶段继续扩概念或把非关键能力提前拉入首批范围。

## Scope

- 本文只定义 vNext 在当前仓库边界内的最小实现切片与阶段计划。
- 本文不改变 MVP single-writer、single-repo、single-adapter 的约束。
- 本文不引入 rich UI、multi-writer、multi-repo、复杂 policy engine、完整人工审批流。
- compiled artifact schema 细节见 `../08-appendix/15-vNext-Compiled-Artifact-Schema-Catalog.md`。

## Definitions

- `Phase 0`：把实现前设计包补齐到可编码状态。
- `Phase 1`：落地最小 compiled artifact / compile / dispatch 闭环。
- `Phase 2`：落地 host-side recovery / fallback / reassign 闭环。
- `测试门`：某阶段进入下一阶段前必须全部通过的测试与验证集合。

## Rules

### 实施总原则

1. 第一批只做对主闭环有直接价值的对象与命令。
2. 优先落地 `spec -> task graph -> run contract -> scaffold -> dispatch` 关键路径。
3. `dossier` 只做非关键派生视图，不得阻塞主闭环。
4. `restore_run`、`soft_cancel`、`hard_kill` fidelity 在真实实验通过前都只能按 fallback 实现。

### 第一批必须落地的对象

Phase 1 必须落地以下对象或对象扩展：

1. `CompilationBatch`
2. `CompiledArtifactMetadata`
3. `PlanRevision` pointer extension
   - `product_spec_ref`
   - `execution_package_ref`
   - `task_graph_ref`
   - `active_dossier_ref` 可延后写入但字段需预留
4. `DispatchIntent` pointer extension
   - `run_contract_ref`
   - `session_scaffold_ref`
5. 最小 artifact 类型：
   - `EvidencePackArtifact`
   - `ProductSpecArtifact`
   - `TaskGraphArtifact`
   - `RunContractArtifact`
   - `SessionScaffoldArtifact`

以下可明确延后：

- `ResearchSprintArtifact`
- `ExecutionPackageArtifact` 的丰富结构
- `ProjectDossierArtifact` 的完整编译器

### 第一批必须落地的命令

Phase 1 必须至少有以下命令：

1. `prepare_compilation_batch`
2. `compile_product_spec`
3. `compile_task_graph`
4. `compile_run_contract`
5. `compile_session_scaffold`
6. `activate_compiled_artifacts`
7. `prepare_dispatch`
8. `confirm_run_started`
9. `submit_handoff`
10. `run_acceptance`

Phase 2 再补：

1. `record_heartbeat_observation`
2. `request_soft_cancel`
3. `request_hard_kill`
4. `start_run_recovery`
5. `rehydrate_and_reassign`

### 第一批必须落地的编译能力

Phase 1 最小编译链要求：

1. 输入：
   - active `Directive`
   - accepted evidence refs
   - active `PlanRevision`
   - selected `Task`
   - selected `DispatchIntent`
2. 输出：
   - `ProductSpecArtifact`
   - `TaskGraphArtifact`
   - `RunContractArtifact`
   - `SessionScaffoldArtifact`
3. 行为：
   - payload durable
   - metadata row durable
   - pointer switch
   - compile batch lineage

### 第一批必须落地的 Codex adapter 能力

Phase 1:

- `launch_run`
- `poll_run`
- `collect_logs`
- `collect_artifacts`

Phase 2:

- `cancel_run`
- `kill_run`
- `restore_run` 作为 probe 接口

### 测试门

#### Gate A: Artifact Compile Gate

必须验证：

1. artifact metadata row 与 payload layout 符合规范
2. payload durable 前不会切 active pointer
3. selective recompile 不会错误复用 stale run contract
4. compile failure 不会产生半激活 pointer

#### Gate B: Dispatch Gate

必须验证：

1. `prepare_dispatch` 只生成一个活跃 `AgentRun(created)`
2. `launch_run` 无 ack 时不会 duplicate dispatch
3. `DispatchIntent` 正确绑定 `run_contract_ref` 与 `session_scaffold_ref`
4. run start 成功后才进入 `running / dispatched / lock active`

#### Gate C: Handoff and Acceptance Gate

必须验证：

1. `submit_handoff` 后 task 进入 `awaiting_acceptance`
2. acceptance 独立于 worker 自报完成
3. rejection / followup 能生成后续 action 而非直接吞掉 handoff

#### Gate D: Recovery and Fallback Gate

必须验证：

1. callback 缺失时，poll-first 仍能观察 run 生命周期
2. timeout 不会直接二次派发
3. soft cancel / hard kill 请求后不会立刻把 run 当成 stopped
4. restore 不可用时，`rehydrate + reassign` 闭环可成立

### 阶段计划

| Phase | 目标 | 必须交付 |
|---|---|---|
| `Phase 0` | 补齐实现前设计包 | 本文、artifact tx 边界、Codex fallback、schema catalog 收口 |
| `Phase 1` | 跑通 compile -> dispatch -> handoff -> acceptance | metadata row、payload root、最小编译器、pointer switch、Codex launch/poll/collect |
| `Phase 2` | 跑通 timeout / ambiguity / cancel / reassign | host-side heartbeat、recovery hold、partial handoff 回收、rehydrate + reassign |
| `Phase 3` | 补强 planning richness 与 dossier | `ExecutionPackageArtifact` 强化、dossier 编译器、验证夹具扩展 |

### 非目标重申

第一批明确不是：

- 多 writer 扩展
- 多 repo 调度
- 人工审批工作流引擎
- 复杂 UI 可视化
- 把 artifact 变成 authoritative runtime state

## Protocol Steps

1. 先完成 `Phase 0` 文档收口，不再新增概念对象。
2. 进入 `Phase 1`：
   - 建表 / schema
   - 实现 artifact compile commands
   - 实现 payload root 写入
   - 实现 pointer activation
   - 接入 Codex launch/poll/collect
3. 通过 Gate A、Gate B、Gate C 后进入 `Phase 2`。
4. 在 `Phase 2` 实现 host-side fallback：
   - heartbeat observation
   - cancel / kill request flow
   - recovery hold
   - `rehydrate + reassign`
5. 通过 Gate D 后，再进入 `Phase 3` 补 dossier 与 richer execution package。

## Acceptance Criteria

- 工程团队能直接按本文拆第一批对象、命令和测试，不再需要自行推断“先做什么”。
- 第一批实现范围明确绑定在关键主闭环，不会被 dossier、rich UI 或多 writer 议题打断。
- 每个阶段都有清晰测试门和进入下一阶段的验收标准。
