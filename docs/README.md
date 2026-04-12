# Hive 设计文档总纲

## Purpose

- 说明本仓库当前承载的两层设计：`MVP implementation package` 与 `vNext long-running autonomous harness`。
- 给出推荐阅读顺序、目录地图和分层边界。
- 明确哪些内容已经收敛、哪些明确转入实现仓、哪些明确不进入当前阶段。

## Scope

- `docs/` 是 Hive 的主设计文档目录。
- 本目录同时服务两类读者：
  - 正在准备实现第一个 Hive 控制平面原型仓的工程师
  - 正在规划 Hive 下一阶段长期自治多-agent harness 的架构设计者
- 本文不替代对象模型、命令协议、执行器契约、恢复协议等分卷。

## Definitions

- `Layer 1 / MVP Control Plane`：当前最接近实现的首版控制平面设计包。
- `Layer 2 / vNext Harness Design`：下一阶段长期自治多-agent 调度控制平面设计。
- `Layer 3 / Explicitly Out of Scope`：明确不进入当前阶段的方向。
- `Worker`：外部执行器角色实例，例如 `Codex`、`Claude Code`。
- `Steering Input`：用户运行中补充的目标、约束、优先级或纠偏输入。

## Rules

### 文档分层

| 层级 | 目标 | 当前状态 | 典型文档 |
|---|---|---|---|
| Layer 1 | 收敛第一个可实现的 Hive 控制平面 | 已收敛为实现前设计包 | `00-overview/03`、`03-state-model/07`、`05-execution/11`、`05-execution/14` |
| Layer 2 | 定义长期自治多-agent harness 的目标架构 | 设计仓收口完成，后续主要进入实现仓与真实 adapter 实验 | `00-overview/05`、`00-overview/06`、`03-state-model/08`、`04-planning/09`、`04-planning/10`、`04-planning/11`、`04-planning/12`、`04-planning/13`、`05-execution/12`、`05-execution/15`、`05-execution/16`、`05-execution/17`、`06-coordination/05`、`07-reliability/14`、`07-reliability/15`、`07-reliability/16` |
| Layer 3 | 明确不在当前阶段扩展的方向 | 明确排除 | multi-writer、multi-repo、复杂 policy engine、rich UI、完整人工审批 |

### 总体边界

- Hive 是控制平面，不是通用 agent。
- Hive 不直接“自己做任务”，而是协调外部执行器完成研究、规划、执行、验证等工作。
- 连续性来自对象状态、事件、checkpoint、handoff artifacts，而不是超长上下文。
- `authoritative object state` 是当前事实来源。
- `Event Log` 是历史与 replay 输入，不是当前事实源。
- `Checkpoint` 是恢复快照，不是事实源。
- acceptance 必须独立于 worker 自报完成。
- `launch_run` 只能写 side effect token / launch markers，不能伪造最终成功状态。

## 建议阅读顺序

### 第一遍：先理解当前 MVP 控制平面

1. `00-overview/01-Hive-Overall-Architecture.md`
2. `00-overview/02-Reference-Architecture.md`
3. `00-overview/03-MVP-Implementation-Blueprint.md`
4. `00-overview/04-Phased-Implementation-Plan.md`
5. `02-governance/03-Drone-Operating-Model.md`
6. `03-state-model/07-MVP-Object-Package.md`
7. `05-execution/11-Control-Plane-API-Contract.md`
8. `05-execution/13-First-Executor-Profile.md`
9. `05-execution/14-Command-Handler-Blueprint.md`
10. `07-reliability/07-Runtime-Directive-Handling.md`
11. `07-reliability/09-End-to-End-Sequence-Scenarios.md`
12. `07-reliability/11-Minimum-Viable-Control-Plane.md`

### 第二遍：再看 vNext 长期自治多-agent harness

1. `00-overview/05-Hive-vNext-Long-Running-Agent-Harness.md`
2. `04-planning/09-Input-to-Spec-and-TaskGraph-Pipeline.md`
3. `04-planning/10-Benchmark-Repo-Research-Protocol.md`
4. `04-planning/11-Project-Dossier-Compilation-Protocol.md`
5. `03-state-model/08-vNext-Compiled-Artifact-Package.md`
6. `04-planning/12-Compilation-Lifecycle-and-Freshness-Protocol.md`
7. `05-execution/15-Agent-Role-Topology-and-Run-Contract.md`
8. `05-execution/16-Executor-Session-Scaffold-Profile.md`
9. `07-reliability/14-Context-Reset-and-Session-Handoff-Protocol.md`
10. `07-reliability/15-User-Interrupt-Replan-and-Preemption-Protocol.md`
11. `07-reliability/16-Run-Termination-and-Reassignment-Matrix.md`
12. `00-overview/06-vNext-Implementation-Gap-Analysis.md`
13. `06-coordination/05-Compiled-Artifact-and-Compilation-Transaction-Boundaries.md`
14. `05-execution/17-Codex-First-Adapter-Fallback-Profile.md`
15. `04-planning/13-vNext-Minimum-Implementation-Slices-and-Phase-Plan.md`
16. `05-execution/12-Executor-Validation-Plan.md`

### 第三遍：按专题补细节

1. `04-planning/03-research-sprint-spec.md`
2. `04-planning/04-evidence-pack-spec.md`
3. `04-planning/05-plan-compilation-protocol.md`
4. `04-planning/06-task-graph-compilation.md`
5. `04-planning/07-Project-Bootstrap-Protocol.md`
6. `04-planning/08-Requirement-Ledger-and-Coverage-Model.md`
7. `05-execution/10-Worker-Session-Bootstrap-Checklist.md`
8. `08-appendix/15-vNext-Compiled-Artifact-Schema-Catalog.md`
9. `07-reliability/04-Incremental-Progress-Discipline.md`
10. `07-reliability/09-Context-Reset-and-Session-Continuity.md`

## 目录结构

```text
docs/
├── README.md
├── 00-overview/
│   ├── 00-文档地图.md
│   ├── 01-Hive-Overall-Architecture.md
│   ├── 02-Reference-Architecture.md
│   ├── 03-MVP-Implementation-Blueprint.md
│   ├── 04-Phased-Implementation-Plan.md
│   ├── 05-Hive-vNext-Long-Running-Agent-Harness.md
│   ├── 06-vNext-Implementation-Gap-Analysis.md
│   ├── design-principles.md
│   └── engineering-laws.md
├── 01-foundation/
│   ├── 01-系统愿景与边界.md
│   ├── 02-核心设计原则.md
│   ├── 03-v0.2-架构加固摘要.md
│   └── 04-系统总体思想框架.md
├── 02-governance/
│   ├── 01-角色职责矩阵.md
│   ├── 02-决策分流规则.md
│   └── 03-Drone-Operating-Model.md
├── 03-state-model/
│   ├── 01-核心对象模型.md
│   ├── 02-对象状态迁移.md
│   ├── 03-event-model.md
│   ├── 04-plan-versioning-and-supersession.md
│   ├── 05-task-graph-model.md
│   ├── 06-Canonical-Enums-and-Identifiers.md
│   ├── 07-MVP-Object-Package.md
│   └── 08-vNext-Compiled-Artifact-Package.md
├── 04-planning/
│   ├── 01-Project-Charter-规范.md
│   ├── 02-Execution-Plan-规范.md
│   ├── 03-research-sprint-spec.md
│   ├── 04-evidence-pack-spec.md
│   ├── 05-plan-compilation-protocol.md
│   ├── 06-task-graph-compilation.md
│   ├── 07-Project-Bootstrap-Protocol.md
│   ├── 08-Requirement-Ledger-and-Coverage-Model.md
│   ├── 09-Input-to-Spec-and-TaskGraph-Pipeline.md
│   ├── 10-Benchmark-Repo-Research-Protocol.md
│   ├── 11-Project-Dossier-Compilation-Protocol.md
│   ├── 12-Compilation-Lifecycle-and-Freshness-Protocol.md
│   └── 13-vNext-Minimum-Implementation-Slices-and-Phase-Plan.md
├── 05-execution/
│   ├── 00-Agent-Session-Protocol.md
│   ├── 01-任务准入规则.md
│   ├── 02-Worker-执行边界.md
│   ├── 03-Handoff-记录规范.md
│   ├── 04-agentrun-lease-heartbeat-protocol.md
│   ├── 05-executor-adapter-contract.md
│   ├── 06-workspace-isolation-model.md
│   ├── 07-path-locking-and-conflict-policy.md
│   ├── 08-handoff-artifact-contract.md
│   ├── 09-Executor-Capability-Matrix.md
│   ├── 10-Lock-Manager-and-Stale-Lock-Recovery.md
│   ├── 10-Worker-Session-Bootstrap-Checklist.md
│   ├── 11-Control-Plane-API-Contract.md
│   ├── 12-Executor-Validation-Plan.md
│   ├── 13-First-Executor-Profile.md
│   ├── 14-Command-Handler-Blueprint.md
│   ├── 15-Agent-Role-Topology-and-Run-Contract.md
│   ├── 16-Executor-Session-Scaffold-Profile.md
│   └── 17-Codex-First-Adapter-Fallback-Profile.md
├── 06-coordination/
│   ├── 01-文件系统协同规则.md
│   ├── 02-Consistency-and-Transaction-Boundaries.md
│   ├── 03-Change-Set-and-Outbox-Contract.md
│   ├── 04-MVP-Storage-Backend-Profile.md
│   └── 05-Compiled-Artifact-and-Compilation-Transaction-Boundaries.md
├── 07-reliability/
│   ├── 01-Checkpoint-与恢复机制.md
│   ├── 02-Evaluation-Gates.md
│   ├── 03-Failure-Recovery-Protocol.md
│   ├── 04-Incremental-Progress-Discipline.md
│   ├── 05-Acceptance-Engine.md
│   ├── 06-Orchestrator-Reconcile-Loop.md
│   ├── 07-Runtime-Directive-Handling.md
│   ├── 08-Recovery-Reconciliation-Checklist.md
│   ├── 09-Context-Reset-and-Session-Continuity.md
│   ├── 09-End-to-End-Sequence-Scenarios.md
│   ├── 10-Invariants-and-Conformance-Rules.md
│   ├── 11-Minimum-Viable-Control-Plane.md
│   ├── 12-Reconcile-Worker-and-Event-Processor-Blueprint.md
│   ├── 13-Conformance-Test-Strategy.md
│   ├── 14-Context-Reset-and-Session-Handoff-Protocol.md
│   ├── 15-User-Interrupt-Replan-and-Preemption-Protocol.md
│   └── 16-Run-Termination-and-Reassignment-Matrix.md
└── 08-appendix/
    ├── 01-术语表.md
    ├── 02-模板索引.md
    ├── 03-Task-Spec-模板.md
    ├── 04-Handoff-模板.md
    ├── 05-Issue-Record-模板.md
    ├── 06-Checkpoint-模板.md
    ├── 07-Acceptance-模板.md
    ├── 08-对象-Schema-草案.md
    ├── 09-事件示例.md
    ├── 10-State-Transition-Tables.md
    ├── 11-Schema-Catalog.md
    ├── 12-Command-and-ChangeSet-Examples.md
    ├── 13-ADR-Index.md
    ├── 14-MVP-Repo-Layout.md
    └── 15-vNext-Compiled-Artifact-Schema-Catalog.md
```

## Design Notes

### 当前已经收敛的内容

- Hive 是控制平面，不是通用 agent。
- Orchestrator 是事件驱动、非常驻、可退出、可从外部状态重建的状态推进器。
- authoritative object state 是当前事实来源。
- Event Log 是历史与 replay 输入，不是当前事实源。
- Checkpoint 是恢复快照，不是事实源。
- acceptance 独立于 worker 自报完成。
- `launch_run` 只能写 launch markers / side effect token。
- MVP 仍维持单仓库、单 writer、单 active plan revision、单 adapter profile、`SQLite + filesystem`。
- Hive-Design 作为设计仓已完成收口，后续主要工作转入 Hive 实现仓。

### 仍留给后续实现与验证的内容

- 把 `Product Spec / Execution Package / Task Graph / Run Contract / Session Scaffold / Dossier` 从设计协议落到实现仓 schema、compiler、validator 和 storage metadata。
- remaining experiments 已统一收口到 `05-execution/12-Executor-Validation-Plan.md`，包括 callback fidelity、delayed exit event handling、restore fidelity、soft cancel fidelity、hard kill fidelity、heartbeat observability、operator command transport form。
- 为 compiled artifacts 补模板生成器、read model 和最小测试夹具，但不改变 truth hierarchy。
- 已补实现前 ADR / spike 收口：artifact ref URI 规范、metadata row 与 payload root 的目录布局、编译批次与 change-set 的事务边界。

### 设计完成状态

- 本仓库在“设计完成”的意义上，已经完成：
  - truth hierarchy 收敛
  - MVP object / command / handler / recovery 主线收敛
  - vNext compiled artifact durable shape 与 transaction boundary 收敛
  - Codex first adapter fallback baseline 收敛
  - 最小实现切片、阶段计划、测试门收敛
- 本仓库在“工程完成”的意义上，还未完成：
  - 尚未进入实现仓落地 schema、handler、adapter、fixture 与 conformance tests
  - 尚未完成真实 adapter experiments

### 下一步动作

- 下一步应进入实现仓，而不是继续撰写新的概念文档。
- 实现仓优先顺序：
  1. 落地 `Phase 1` schema / commands / handlers / compile pipeline
  2. 建立 fake adapter 与 e2e fixtures
  3. 执行 `05-execution/12-Executor-Validation-Plan.md` 中的真实 adapter experiments
  4. 仅在实验结果要求时，回写 capability matrix 与 fallback 边界

### 封箱口径

- Hive-Design 现在应按“设计仓已完成、进入实现移交”理解，而不是继续作为概念扩写仓。
- canonical 实验 backlog 只有 `05-execution/12-Executor-Validation-Plan.md` 一处。
- 未在该 backlog 中的问题，默认不再视为设计仓 open gap。

### 明确不进入当前阶段的内容

- multi-writer distributed control plane
- multi-repo federation
- 复杂 policy engine
- rich UI / dashboard
- 完整人工审批工作流

## 路径兼容说明

- `02-governance/03-Drone-Operating-Model.md` 保留旧文件名，但正文统一使用 `Orchestrator`。
- `Queen` 若在旧路径或旧文档中出现，只表示升级/裁决职责，不表示一个魔法角色或长驻大 agent。
- `09-Context-Reset-and-Session-Continuity.md` 保留为连续性概览；完整协议以 `14-Context-Reset-and-Session-Handoff-Protocol.md` 为准。

## Acceptance Criteria

- 新读者能在 5 分钟内看懂本仓库为什么分成 Layer 1、Layer 2、Layer 3。
- 新读者能明确知道先看 MVP，再看 vNext。
- 读者能明确知道 Hive 协调外部执行器，而不是把所有智能塞进单个模型会话。
