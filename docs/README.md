# Hive 设计文档总纲（MVP Implementation Package Draft v0.6）

> 目标：把 Hive 从“implementation contract draft”继续收敛为“first implementation 可直接开工的实现前设计包”，回答首版控制平面的目录结构、对象包、handler 映射、黄金路径、失败补偿和分阶段开工方式。

## 1. 文档使用方式

- `docs/` 是 Hive 的主设计文档目录。
- 文档分为三层：
  - 原则层：系统定位、工程法则、角色边界
  - 协议层：对象、事件、计划编译、执行、恢复、验收、调度、实现蓝图
  - 模板层：schema、模板、事件示例、ADR、repo layout
- 阅读时优先看协议层中的实现蓝图章节，原则层用于理解边界，模板层用于生成实现骨架与测试夹具。

## 2. 建议阅读顺序

1. `00-overview`：文档地图、总体架构、参考架构、MVP 实现蓝图、分阶段实施计划、工程法则
   - 先读 `engineering-laws.md`
   - 再读 `01-Hive-Overall-Architecture.md`
   - 再读 `02-Reference-Architecture.md`
   - 再读 `03-MVP-Implementation-Blueprint.md`
   - 再读 `04-Phased-Implementation-Plan.md`
   - 再读 `00-文档地图.md`
2. `01-foundation`：系统定位、原则、总体思想框架
3. `02-governance`：角色边界、决策路由、Orchestrator 运行模型
4. `03-state-model`：核心对象、状态迁移、事件模型、Plan Revision、Task Graph、canonical enums / identifiers、MVP 对象包
   - 先读 `06-Canonical-Enums-and-Identifiers.md`
   - 再读 `07-MVP-Object-Package.md`
5. `04-planning`：Research Sprint、Evidence Pack、Brief / Charter / Execution Plan 编译链
6. `06-coordination`：状态对象、目录语义、一致性边界、change-set / outbox、MVP storage backend profile
7. `05-execution`：Session、Task、Worker、AgentRun、执行器适配、能力矩阵、API contract、first executor profile、command handler mapping、执行器验证计划
   - 先读 `11-Control-Plane-API-Contract.md`
   - 再读 `14-Command-Handler-Blueprint.md`
8. `07-reliability`：Checkpoint、Acceptance、Reconcile Loop、Golden Path、Recovery Checklist、MVP 控制平面、worker blueprint、conformance test strategy
   - 先读 `09-End-to-End-Sequence-Scenarios.md`
   - 再读 `11-Minimum-Viable-Control-Plane.md`
   - 再读 `13-Conformance-Test-Strategy.md`
9. `08-appendix`：schema catalog、命令示例、事件示例、状态迁移总表、ADR、MVP repo layout

## 3. 目录结构

```text
docs/
├── README.md
├── 00-overview/
│   ├── 00-文档地图.md
│   ├── 01-Hive-Overall-Architecture.md
│   ├── 02-Reference-Architecture.md
│   ├── 03-MVP-Implementation-Blueprint.md
│   ├── 04-Phased-Implementation-Plan.md
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
│   └── 07-MVP-Object-Package.md
├── 04-planning/
│   ├── 01-Project-Charter-规范.md
│   ├── 02-Execution-Plan-规范.md
│   ├── 03-research-sprint-spec.md
│   ├── 04-evidence-pack-spec.md
│   ├── 05-plan-compilation-protocol.md
│   └── 06-task-graph-compilation.md
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
│   ├── 11-Control-Plane-API-Contract.md
│   ├── 12-Executor-Validation-Plan.md
│   ├── 13-First-Executor-Profile.md
│   └── 14-Command-Handler-Blueprint.md
├── 06-coordination/
│   ├── 01-文件系统协同规则.md
│   ├── 02-Consistency-and-Transaction-Boundaries.md
│   ├── 03-Change-Set-and-Outbox-Contract.md
│   └── 04-MVP-Storage-Backend-Profile.md
├── 07-reliability/
│   ├── 01-Checkpoint-与恢复机制.md
│   ├── 02-Evaluation-Gates.md
│   ├── 03-Failure-Recovery-Protocol.md
│   ├── 04-Incremental-Progress-Discipline.md
│   ├── 05-Acceptance-Engine.md
│   ├── 06-Orchestrator-Reconcile-Loop.md
│   ├── 07-Runtime-Directive-Handling.md
│   ├── 08-Recovery-Reconciliation-Checklist.md
│   ├── 09-End-to-End-Sequence-Scenarios.md
│   ├── 10-Invariants-and-Conformance-Rules.md
│   ├── 11-Minimum-Viable-Control-Plane.md
│   ├── 12-Reconcile-Worker-and-Event-Processor-Blueprint.md
│   └── 13-Conformance-Test-Strategy.md
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
    └── 14-MVP-Repo-Layout.md
```

## 4. 阅读分层说明

### 原则层

- `00-overview/`
- `01-foundation/`
- `02-governance/01-角色职责矩阵.md`
- `02-governance/02-决策分流规则.md`

### 协议层

- `02-governance/03-Drone-Operating-Model.md`
- `03-state-model/`
- `04-planning/`
- `05-execution/`
- `06-coordination/`
- `07-reliability/`

### 模板层

- `08-appendix/`

## 5. 当前文档重点

- Hive 是控制平面，不是通用 agent。
- Orchestrator 是事件驱动状态机，不是长驻大模型会话。
- Worker 是可丢弃执行单元，不是事实来源。
- Task、AgentRun、Handoff、Acceptance、Checkpoint 必须分离建模。
- Event Log、Object State、Checkpoint 已有明确层级：当前事实、历史、恢复快照。
- canonical enums、event names、field names、ID prefixes 已集中到单一 registry。
- change-set / outbox 已收敛为控制平面的核心持久化协议。
- 当前重点不再是泛化概念，而是收敛实现前设计包：
  - `03-MVP-Implementation-Blueprint.md`
  - `04-Phased-Implementation-Plan.md`
  - `03-state-model/07-MVP-Object-Package.md`
  - `05-execution/14-Command-Handler-Blueprint.md`
  - `07-reliability/09-End-to-End-Sequence-Scenarios.md`
- 项目连续性来自外部状态，不来自超长上下文。

## 6. 路径兼容说明

- `02-governance/03-Drone-Operating-Model.md` 保留旧文件名以保持路径连续性。
- 该文件正文已统一使用 `Orchestrator`，`Drone` 仅作为历史命名保留在路径层。
