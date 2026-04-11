# 11 Project Dossier Compilation Protocol

## Purpose

- 定义 `Project Dossier / Project Book` 这类长文档派生视图的编译协议。
- 让 Hive 可以产出“像一本书一样”的项目设计与执行文档，同时不破坏 runtime truth 边界。
- 明确 dossier 的章节结构、刷新触发、输入映射和使用边界。

## Scope

- 本文覆盖 `Project Dossier / Project Book` 的结构、编译输入、刷新策略和使用规则。
- 本文不把 dossier 升级为 authoritative object，也不允许调度层直接解析 dossier 做运行决策。
- bootstrap 阶段对 dossier 的定位见 `07-Project-Bootstrap-Protocol.md`。
- vNext 规划主链见 `09-Input-to-Spec-and-TaskGraph-Pipeline.md`。

## Definitions

- `Project Dossier`：面向人类阅读的结构化长文档视图，汇总目标、边界、计划、覆盖、风险与当前进展。
- `Project Book`：当 dossier 以更完整、更长期的形式组织时的别名；协议上与 `Project Dossier` 同类。
- `Stable Section`：主要由 `Brief / Charter / accepted decisions` 驱动，更新频率较低的章节。
- `Evolving Section`：主要由 `Execution Plan / Task Graph / Requirement Ledger / Handoff summary` 驱动，更新频率较高的章节。
- `Compilation Stamp`：标识 dossier 当前编译使用的 plan revision、checkpoint、handoff summary 与时间戳。

## Rules

### Dossier 不是运行态事实源

- dossier 是 compiled view，不是 runtime source of truth。
- 调度、恢复、验收、重规划必须读取结构化对象，而不是回读 dossier 文本段落。
- dossier 中若存在过期内容，必须通过重新编译修正，而不是人工在自由文本里直接改 runtime truth。

### Compilation Inputs

dossier 编译至少允许使用以下输入：

- `Directive` / `Brief` / `Product Spec`
- `Charter`
- `Execution Plan` / `PlanRevision`
- `Requirement Ledger`
- `Task Graph` 摘要
- `Evidence Pack`
- open `Issue` / pending `Decision`
- 最新 `Checkpoint`
- 最近 `Handoff` / `Partial Handoff` 摘要

规则：

- `Stable Section` 优先使用 stable inputs。
- `Evolving Section` 优先使用当前 active plan revision 与 ledger 状态。
- 未被采纳的候选方案只能出现在 evidence / alternatives 章节，不能写成已决事实。

### 推荐章节结构

推荐章节如下：

| 章节 | 主要来源 | 类型 | 说明 |
|---|---|---|---|
| 1. 项目摘要 | `Brief / Product Spec` | stable | 项目目标、核心价值、当前阶段 |
| 2. 范围与非目标 | `Brief / Charter` | stable | include / exclude、边界声明 |
| 3. 不变量与架构原则 | `Charter / accepted decisions` | stable | 不得违反的原则与架构约束 |
| 4. 关键术语与对象关系 | `Brief / Charter / model refs` | stable | 帮助读者对齐语义 |
| 5. 当前执行策略 | `Execution Plan / PlanRevision` | evolving | 阶段、工作线、里程碑、replan hooks |
| 6. 需求覆盖视图 | `Requirement Ledger` | evolving | 哪些能力已 captured / planned / accepted / blocked |
| 7. 任务图与活跃工作线摘要 | `Task Graph / active tasks / active runs` | evolving | 不是全量 runtime dump，而是人类可读摘要 |
| 8. 研究与 benchmark 摘要 | `Evidence Pack` | evidence | claims、options、risks、未采纳候选方案 |
| 9. 当前进展与最近交接 | `Checkpoint / Handoff summary` | evolving | 最近完成、部分完成、未决风险 |
| 10. 开放问题与待决策项 | open `Issue` / pending `Decision` | evidence | 当前阻塞与待确认事项 |
| 11. 风险、恢复与重规划观察 | `Issue / RecoveryAction / plan hooks` | evolving | 风险面与何时可能 replan |
| 12. 附录与来源索引 | refs catalog | appendix | 关键 artifact、spec、evidence、handoff refs |

### Stable vs Evolving 编译规则

- `Stable Section` 不应因单个 task 状态变化而频繁刷新。
- `Evolving Section` 允许随 plan revision、ledger、checkpoint、handoff summary 更新。
- 同一 dossier 中必须显式区分 stable 内容与 evolving 内容，避免读者误把临时策略当宪章。

### Refresh Trigger Rule

以下情况应刷新 dossier：

- bootstrap 完成并形成首个稳定 dossier
- 新的 active `PlanRevision` 被采纳
- 用户 steering input 导致显著 replan / supersession
- Requirement Ledger 出现重要覆盖状态变化
- 进入新的阶段边界或里程碑边界
- 需要面向人类做阶段汇报、handoff 或外部审阅

以下情况通常不需要刷新 dossier：

- 单次 heartbeat
- 单个 run 的临时日志变化
- 尚未影响叙事层的局部 task 状态抖动
- duplicate event、no-op reconcile、瞬时 recovery hold

### Freshness Rule

每次 dossier 编译都必须写出 `Compilation Stamp`，至少包括：

- `compiled_at`
- `active_plan_revision_id`
- `requirement_ledger_id`
- `latest_checkpoint_id`
- `latest_handoff_summary_ref`

规则：

- 若 dossier 落后于当前 active plan revision，应显式标记 stale，而不是默默假装最新。
- dossier 的章节应尽量带来源 refs，保证读者能回到结构化对象。

### 使用边界

dossier 可以用于：

- 人类阅读和理解项目全貌
- 阶段性汇报
- 跨 session / 跨角色 handoff 的高层总览
- 对外沟通当前设计与执行状态

dossier 不得用于：

- 直接驱动 scheduler 选择 ready task
- 直接替代 `Task Graph / Run Contract / Requirement Ledger`
- 直接作为 acceptance 或 recovery 的事实输入

### Mapping Rule

`Project Dossier` 与规划对象的映射必须清晰：

| 源对象 | dossier 中的典型落点 |
|---|---|
| `Product Spec / Brief` | 项目摘要、范围、成功标准 |
| `Charter` | 不变量、架构原则、边界 |
| `Execution Plan / PlanRevision` | 当前执行策略、里程碑、工作线 |
| `Requirement Ledger` | 需求覆盖视图、未完成能力 |
| `Task Graph` | 活跃工作线摘要、依赖说明 |
| `Evidence Pack` | benchmark 摘要、候选方案、风险 |
| `Issue / Decision` | 开放问题、待决策项 |
| `Checkpoint / Handoff` | 最近进展、当前交接状态 |

## Protocol Steps

1. 收集当前 compilation inputs。
2. 先编译 stable sections，再叠加 evolving sections。
3. 对 `Evidence Pack`、open issues、recent handoffs 生成摘要性章节。
4. 为每个章节写入来源 refs 或 stamp 信息。
5. 生成 `Compilation Stamp`。
6. 发布 dossier artifact ref，供人类阅读与 review。

## State / Schema

```yaml
project_dossier:
  dossier_id: dossier_main
  compiled_at: 2026-04-11T15:30:00Z
  compilation_stamp:
    active_plan_revision_id: plan_rev_12
    requirement_ledger_id: req_ledger_main
    latest_checkpoint_id: checkpoint_20260411_05
    latest_handoff_summary_ref: handoff_summary_20260411_03
  sections:
    stable:
      - project_summary
      - scope_and_non_goals
      - invariants
    evolving:
      - execution_strategy
      - coverage_view
      - active_worklines
      - progress_summary
    evidence:
      - benchmark_summary
      - open_issues
```

## Anti-patterns

- 把 dossier 当运行时事实源，再从长文档里反向摘任务。
- 每个 task 状态一变就重写整本 dossier，导致成本过高且噪声巨大。
- 把未采纳的候选方案写成既定决策。
- 只写 narrative，不写 plan revision、checkpoint、handoff 等 freshness refs。

## Acceptance Criteria

- 读者能明确知道 dossier 是从哪些结构化对象编译出来的。
- 读者能区分 stable sections 与 evolving sections。
- 文档明确规定了何时需要刷新 dossier，何时不需要。
- 调度与恢复仍然回到结构化对象，而不是依赖 dossier 文本。
