# Hive 设计文档总纲（Reference Architecture Draft v0.3）

> 目标：把 Hive 从“协议级工程设计规范”继续收敛为“控制平面参考架构草案”。

## 1. 文档使用方式

- `docs/` 是 Hive 的主设计文档目录。
- 文档分为三层：
  - 原则层：系统定位、工程法则、角色边界
  - 协议层：对象、事件、计划编译、执行、恢复、验收、调度
  - 模板层：schema、模板、事件示例
- 阅读时优先看协议层，原则层用于理解边界，模板层用于落地实现。

## 2. 建议阅读顺序

1. `00-overview`：文档地图、总体架构、参考架构、工程法则
   - 先读 `engineering-laws.md`
   - 再读 `01-Hive-Overall-Architecture.md`
   - 再读 `02-Reference-Architecture.md`
   - 再读 `00-文档地图.md`
2. `01-foundation`：系统定位、原则、总体思想框架
3. `02-governance`：角色边界、决策路由、Orchestrator 运行模型
4. `03-state-model`：核心对象、状态迁移、事件模型、Plan Revision、Task Graph
5. `04-planning`：Research Sprint、Evidence Pack、Brief / Charter / Execution Plan 编译链
6. `05-execution`：Session、Task、Worker、AgentRun、执行器适配、能力矩阵、工作区、锁、Handoff 契约
7. `06-coordination`：状态对象、目录语义、存储分层、一致性边界与事务边界
8. `07-reliability`：Checkpoint、Evaluation、Failure Recovery、Acceptance、Reconcile Loop、Runtime Directive、Recovery Checklist、端到端场景
9. `08-appendix`：模板、schema 草案、事件示例、状态迁移总表

## 3. 目录结构

```text
docs/
├── README.md
├── 00-overview/
│   ├── 00-文档地图.md
│   ├── 01-Hive-Overall-Architecture.md
│   ├── 02-Reference-Architecture.md
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
│   └── 05-task-graph-model.md
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
│   └── 10-Lock-Manager-and-Stale-Lock-Recovery.md
├── 06-coordination/
│   ├── 01-文件系统协同规则.md
│   └── 02-Consistency-and-Transaction-Boundaries.md
├── 07-reliability/
│   ├── 01-Checkpoint-与恢复机制.md
│   ├── 02-Evaluation-Gates.md
│   ├── 03-Failure-Recovery-Protocol.md
│   ├── 04-Incremental-Progress-Discipline.md
│   ├── 05-Acceptance-Engine.md
│   ├── 06-Orchestrator-Reconcile-Loop.md
│   ├── 07-Runtime-Directive-Handling.md
│   ├── 08-Recovery-Reconciliation-Checklist.md
│   └── 09-End-to-End-Sequence-Scenarios.md
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
    └── 10-State-Transition-Tables.md
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
- 项目连续性来自外部状态，不来自超长上下文。

## 6. 路径兼容说明

- `02-governance/03-Drone-Operating-Model.md` 保留旧文件名以保持路径连续性。
- 该文件正文已统一使用 `Orchestrator`，`Drone` 仅作为历史命名保留在路径层。
