# Hive 设计文档总纲（Draft v0.1）

> 目标：先建立“像一本书”的文档骨架，后续可持续增量完善。

## 1. 文档使用方式

- `docs/` 作为 Hive 设计文档主目录。
- 采用“总纲 + 分卷 + 章节”结构：
  - 总纲负责导航与阅读顺序；
  - 分卷负责主题边界；
  - 章节负责可执行细节与约束。

## 2. 建议阅读顺序

1. `00-overview`：项目背景与阅读地图
   - 先读 `engineering-laws.md`
2. `01-foundation`：核心原则与术语
3. `02-governance`：角色边界与决策路由
4. `03-state-model`：对象模型与状态机
5. `04-planning`：计划体系（Charter / Execution Plan）
6. `05-execution`：任务准入、执行与交接
7. `06-coordination`：文件系统协同约束
8. `07-reliability`：检查点、恢复与可持续运行
9. `08-appendix`：模板、示例与未来扩展

## 3. 目录结构（初版）

```text
docs/
├── README.md
├── 00-overview/
│   ├── 00-文档地图.md
│   ├── design-principles.md
│   └── engineering-laws.md
├── 01-foundation/
│   ├── 01-系统愿景与边界.md
│   ├── 02-核心设计原则.md
│   ├── 03-v0.2-架构加固摘要.md
│   └── 04-系统总体思想框架.md
├── 02-governance/
│   ├── 01-角色职责矩阵.md
│   └── 02-决策分流规则.md
├── 03-state-model/
│   ├── 01-核心对象模型.md
│   └── 02-对象状态迁移.md
├── 04-planning/
│   ├── 01-Project-Charter-规范.md
│   └── 02-Execution-Plan-规范.md
├── 05-execution/
│   ├── 00-agent-session-protocol.md
│   ├── 01-任务准入规则.md
│   ├── 02-Worker-执行边界.md
│   └── 03-Handoff-记录规范.md
├── 06-coordination/
│   └── 01-文件系统协同规则.md
├── 07-reliability/
│   ├── 01-Checkpoint-与恢复机制.md
│   ├── 03-evaluation-gates.md
│   ├── 04-failure-recovery-protocol.md
│   └── 05-incremental-progress-discipline.md
└── 08-appendix/
    ├── 01-术语表.md
    └── 02-模板索引.md
```

## 4. 与 v0.2 Amendment 的关系

本骨架已将你提供的《Hive Architecture Amendments (v0.2 Design Reinforcement)》映射到章节中：

- 对象模型：`03-state-model/`
- Plan 拆分：`04-planning/`
- Session 协议 + 任务准入 + Worker 边界：`05-execution/`
- 决策分流 + Orchestrator 职责：`02-governance/`
- 文件系统规则：`06-coordination/`
- Checkpoint + Evaluation + Failure Recovery + Incremental Progress：`07-reliability/`

## 5. 下一步建议（可选）

- 先定“必须先写完”的 6 个章节：
  - 系统总体思想框架
  - 核心对象模型
  - 对象状态迁移
  - 任务准入规则
  - 决策分流规则
  - 文件系统协同规则
- 每章统一采用：目的、输入、规则、反例、验收标准 五段式模板。
