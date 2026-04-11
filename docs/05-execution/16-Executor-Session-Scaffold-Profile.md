# 16 Executor Session Scaffold Profile

## Purpose

- 定义 Hive 为外部执行器 session 提供的标准化脚手架产物集合。
- 把“initializer 首轮要留下什么、后续 session 启动时应先读什么”从零散约束提升为统一 profile。
- 让新 session 即使在 context reset、worker 替换或跨多轮执行后，仍能快速恢复定向。

## Scope

- 本文覆盖 session scaffold artifacts 的最小集合、刷新时机、与 authoritative objects 的关系。
- 本文不替代 `Checkpoint`、`Handoff`、`Requirement Ledger`、`TaskSpec` 等 authoritative 或 protocol-level objects。
- durable carrier 与 pointer 挂载方式见 `../03-state-model/08-vNext-Compiled-Artifact-Package.md`。
- freshness gate 与 selective recompile 见 `../04-planning/12-Compilation-Lifecycle-and-Freshness-Protocol.md`。
- Worker bootstrap 顺序见 `10-Worker-Session-Bootstrap-Checklist.md`。
- context reset handoff 见 `../07-reliability/14-Context-Reset-and-Session-Handoff-Protocol.md`。

## Definitions

- `Session Scaffold`：为外部执行器新 session 提供的低摩擦 bootstrap 输入集合。
- `Coverage View`：从 `Requirement Ledger` 派生的机器可读覆盖摘要。
- `Recent Progress Digest`：从最近 checkpoint、handoff、partial handoff、acceptance 摘要出来的近期进展视图。
- `Workspace Bootstrap Entry`：帮助 worker 进入正确 workspace、确认命令入口与环境前提的启动信息。
- `Baseline Smoke-Check Contract`：新 session 启动时应优先执行的最小健康检查契约。
- `Read-First Manifest`：对本轮 session 最先必须读取的 refs 的有序清单。

## Rules

### Scaffold 不是 authoritative truth

- session scaffold artifacts 只是 bootstrap input，不是 runtime truth。
- 若 scaffold 与 authoritative object state 冲突，必须以 `Checkpoint / PlanRevision / Requirement Ledger / TaskSpec / Handoff` 为准。
- scaffold 缺失或过期时，worker 必须回退到 authoritative objects，不得凭 scaffold 猜测。

### Canonical Carrier Rule

- durable 形态中的 session scaffold 应由 `SessionScaffoldArtifact` 承载。
- canonical pointer 应挂在 `DispatchIntent.session_scaffold_ref`，并与 `run_contract_ref` 成对出现。
- `SessionScaffoldArtifact` 的 payload 可细分为多个子文档，但 metadata row 必须能独立表达 freshness、lineage 和 supersession。

### 最小脚手架产物集合

每个 active workline 至少应提供以下 5 类 scaffold：

1. `requirement_feature_coverage_view`
2. `recent_progress_digest`
3. `workspace_bootstrap_entry`
4. `baseline_smoke_check_contract`
5. `read_first_manifest`

### Artifact Profile

| Artifact | 主要输入 | 作用 | 典型格式 |
|---|---|---|---|
| `requirement_feature_coverage_view` | `Requirement Ledger`、accepted followups | 告诉 session 还有哪些能力未完成、哪些已 blocked / accepted | JSON / YAML |
| `recent_progress_digest` | 最近 `Checkpoint`、`Handoff`、`Partial Handoff`、`Acceptance` | 告诉 session 最近做了什么、还剩什么、当前风险是什么 | Markdown + structured summary |
| `workspace_bootstrap_entry` | `workspace_ref`、repo root、命令入口、环境前提 | 让 session 快速定位 cwd、worktree、必要入口命令 | YAML / shell entry ref |
| `baseline_smoke_check_contract` | `TaskSpec`、validation baseline、system invariants | 让 session 开工前先验证当前环境没有被前一轮搞坏 | YAML |
| `read_first_manifest` | `Checkpoint`、`PlanRevision`、`TaskSpec`、关键 evidence refs | 规定新 session 的最小阅读顺序 | YAML / JSON |

### 与 authoritative objects 的关系

必须明确以下映射：

| Scaffold Artifact | 派生自哪些 authoritative / protocol objects |
|---|---|
| `requirement_feature_coverage_view` | `Requirement Ledger` |
| `recent_progress_digest` | `Checkpoint`、`Handoff`、`Partial Handoff`、`Acceptance` |
| `workspace_bootstrap_entry` | `DispatchIntent.workspace_plan`、`TaskSpec`、workspace registry |
| `baseline_smoke_check_contract` | `TaskSpec.validation`、system baseline、最近健康状态 |
| `read_first_manifest` | `Checkpoint`、`PlanRevision`、`TaskSpec`、evidence refs、session handoff artifact |

规则：

- 这些脚手架必须是可重编译的 derived artifacts。
- 不允许在脚手架中引入只存在于聊天上下文里的隐含知识。

### Coverage View Rule

- `Coverage View` 必须突出：
  - 未完成能力
  - 已 blocked / in_progress / accepted 的能力
  - 与当前 session 最相关的 requirement slice
- 它的目标是阻止执行器“看见一些进展就宣布项目完成”。
- `Coverage View` 不能替代全量 `Requirement Ledger`；它只是高频摘要。

### Recent Progress Digest Rule

- `Recent Progress Digest` 必须基于 durable records，而不是自由回忆。
- 它至少应包含：
  - 最近完成或部分完成的工作
  - 最近一次未完成的原因
  - 当前主要风险
  - 推荐下一步
- 若最近 progress 只有噪声级变化，不必刷新 digest。

### Workspace Bootstrap Entry Rule

- `Workspace Bootstrap Entry` 必须明确：
  - `workspace_ref`
  - 目标 cwd / repo root
  - 必要命令入口
  - 只读 / 可写边界
  - 若 workspace 已回收，应如何 fallback
- 它可以是 manifest，也可以是一个 entry script ref，但不得成为唯一事实源。

### Baseline Smoke-Check Contract Rule

- `Baseline Smoke-Check Contract` 是 session 开工前的最小健康检查，不是完整 acceptance。
- 它至少应覆盖：
  - workspace 可访问
  - repo 状态可读
  - 关键入口命令存在
  - 当前 workline 的最小 happy path 未被破坏
- smoke-check 失败时，worker 应先上报 blocker / recovery risk，而不是直接开始新改动。

### Read-First Manifest Rule

- `Read-First Manifest` 必须给出新 session 的固定最小阅读顺序。
- 它至少应引用：
  - 最新 `Checkpoint`
  - 当前 `PlanRevision`
  - 当前 `TaskSpec / Run Contract`
  - 最近 `Handoff / Partial Handoff`
  - 当前最关键 evidence refs
- 若 context reset 前已有 `session handoff artifact`，必须把其中的 `read_first` 项合并进来。

### Refresh Trigger Rule

以下情况应刷新相关 scaffold artifacts：

- 新 `Checkpoint` 写出
- 新 `Handoff` / `Partial Handoff` 被接纳
- active `PlanRevision` 更新
- `TaskSpec` / `Run Contract` 被 supersede
- workspace 绑定发生变化
- 发生 context reset 或 worker replacement

以下情况通常不需要刷新全套 scaffold：

- 单次 heartbeat
- 噪声级日志变化
- 未改变 bootstrap 输入的重复 reconcile

## Protocol Steps

1. bootstrap 或 replan 结束后，编译第一版 session scaffold artifacts。
2. 派发 `Run Contract` 时，将相应 scaffold refs 绑定到 dispatch input。
3. worker session 启动后，先读取 `read_first_manifest`。
4. worker 依次读取 coverage view、progress digest、workspace bootstrap entry、smoke-check contract。
5. worker 再按 `10-Worker-Session-Bootstrap-Checklist.md` 读取 authoritative objects。
6. 若 scaffold 缺失、过期或与 authoritative state 冲突，则写 blocker / issue 并停止盲做。

## State / Schema

```yaml
executor_session_scaffold:
  scaffold_id: scaffold_run_exec_15
  bound_run_contract_id: rc_20260411_07
  artifacts:
    requirement_feature_coverage_view: artifacts/scaffold/coverage_view_07.json
    recent_progress_digest: artifacts/scaffold/progress_digest_07.md
    workspace_bootstrap_entry: artifacts/scaffold/workspace_entry_07.yaml
    baseline_smoke_check_contract: artifacts/scaffold/smoke_check_07.yaml
    read_first_manifest: artifacts/scaffold/read_first_07.yaml
  source_refs:
    checkpoint_id: checkpoint_20260411_09
    plan_revision_id: plan_rev_08
    requirement_ledger_id: req_ledger_main
    latest_handoff_id: handoff_run_exec_14
    task_spec_id: task_auth_ui_04
```

## Anti-patterns

- 只给 worker 一个模糊 prompt，不给任何结构化 bootstrap inputs。
- 把 progress digest 当事实源，跳过 checkpoint / handoff / task spec。
- smoke-check 合同过大，变成完整 acceptance 套件，导致启动成本过高。
- workspace bootstrap 信息只存在于上一轮聊天记录里。

## Acceptance Criteria

- 新 session 能明确知道应该先读哪些 refs、先做哪些最小检查。
- session scaffold artifacts 能覆盖 requirement coverage、recent progress、workspace bootstrap、baseline smoke-check、read-first refs 五个方面。
- 文档明确指出这些脚手架产物是 derived bootstrap inputs，不是 authoritative runtime truth。
- worker 替换、context reset、partial handoff 后仍可基于 scaffold + authoritative objects 重新定向。
