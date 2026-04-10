# 01 Hive Overall Architecture

## Purpose

- 用一张图说明 Hive 的整体运行方式。
- 让读者快速理解调度、执行、状态回写、冲突升级链路。

## Mermaid Diagram

### Hive Overall Architecture

```mermaid
flowchart TD
    Q["Queen\n需求方向 / 关键裁决"]
    D["Orchestrator\n调度 / 状态推进 / 决策分流"]
    KB["Hive Knowledge Base\n外部状态 / 共享知识"]

    I["Idea"]
    B["Brief"]
    P["Plan"]
    PH["Phase"]
    T["Task"]

    W1["Worker Bee A"]
    W2["Worker Bee B"]
    W3["Worker Bee C"]

    H["Handoff"]
    DEC["Decision"]
    ISS["Issue / Blocker"]
    CP["Checkpoint"]

    Q -->|提出需求| I
    Q -->|关键决策| D

    I --> B --> P --> PH --> T
    P --> KB
    PH --> KB
    T --> KB

    D -->|读取状态 / 派发任务| KB
    D -->|调度| W1
    D -->|调度| W2
    D -->|调度| W3

    T -->|Task 引用| W1
    T -->|Task 引用| W2
    T -->|Task 引用| W3

    W1 -->|写回| H
    W2 -->|写回| H
    W3 -->|写回| H

    W1 -->|阻塞 / 异常| ISS
    W2 -->|阻塞 / 异常| ISS
    W3 -->|阻塞 / 异常| ISS

    H --> KB
    ISS --> KB

    D -->|生成 / 更新| DEC
    D -->|写入| CP
    DEC --> KB
    CP --> KB
    KB -->|反馈状态| D
    D -->|Requirement conflict 升级| Q
```

## Rules

- Queen 提供需求与关键决策。
- Orchestrator 负责调度、状态推进、决策分流。
- Worker Bees 执行具体 Task。
- Hive Knowledge Base 承载外部状态与共享知识。
- Worker 完成后必须写回 Handoff、Issue 与 Artifact。
- Orchestrator 基于运行结果写出 Checkpoint。
- Orchestrator 根据结果更新状态并决定下一步。

## Acceptance Criteria

- 读者应能在 30 秒内理解 Hive 的主运行链路。
- 图中必须能看出需求输入、任务派发、结果回写、状态更新、冲突升级。

> Hive 连续性来自外部状态，不是来自 agent context。
