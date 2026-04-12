# Hive Design

Hive 是一个面向外部执行器的控制平面设计仓。它当前同时承载两层设计：

1. `MVP implementation package`
   说明第一个 Hive 控制平面原型仓如何实现单 writer、单仓库、单 adapter、`SQLite + filesystem` 的闭环。
2. `vNext long-running autonomous multi-agent harness`
   说明 Hive 如何把一句高层需求扩展为研究、规划、执行、验收、恢复、重规划与 context reset 的长期自治工作流，但仍然把执行留给 `Codex`、`Claude Code` 等外部执行器。

这个仓库不是实现仓，不包含业务代码实现。它的目标是把 Hive 的边界写清楚：

- Hive 是 `control plane`，不是通用 agent。
- Hive 不把连续性寄托在单个超长模型会话里，而是把连续性外置到 `authoritative object state`、事件、checkpoint 和 handoff artifacts。
- 外部执行器负责调研、实现、验证等具体工作；Hive 负责输入收敛、规划、派发、状态推进、验收、恢复、重规划和 context reset。
- `authoritative object state` 是当前事实来源。
- `Event Log` 是历史与 replay 输入，不是当前事实源。
- `Checkpoint` 是恢复快照，不是事实源。
- acceptance 必须独立于 worker 自报完成。
- `launch_run` 只能写 side effect token / launch markers，不能伪造最终成功状态。
- Orchestrator 必须是事件驱动、非常驻、可退出、可从外部状态重建。

当前它已经基本完成“设计仓”使命：

- 直接可实现的部分已经收口为实现前设计包；
- 不能靠纯设计关闭的部分，已经统一收口为真实 adapter experiment backlog；
- 下一步应进入实现仓落地，而不是继续扩写新概念文档。

## 现在是什么

当前仓库最接近实现的是第 1 层：`MVP control plane`。它回答：

- 第一个控制平面原型仓要有哪些对象、命令、handler、checkpoint、recovery 和 adapter 边界
- 如何在单 writer 前提下保证 change-set / outbox / event log / checkpoint 一致
- 如何让 `Directive -> PlanRevision -> Task -> AgentRun -> Handoff -> Acceptance -> Checkpoint` 跑通

## 下一步会变成什么

第 2 层是 `vNext long-running autonomous harness`。它回答：

- 用户一句话如何先进入 research / evidence / spec / task graph / run contract，而不是直接扔给执行 agent
- 同类仓库 / benchmark repo 调研如何受控进入 research，并被编译为 evidence
- `Product Spec / Execution Package / Task Graph / Run Contract / Session Scaffold` 如何作为 durable compiled artifacts 被持久化并挂到 `PlanRevision / DispatchIntent`
- 这条编译链如何做 freshness、失效判定、selective recompile 与 active pointer 切换
- 面向人阅读的 `Project Dossier / Project Book` 如何从结构化对象编译出来，而不是反向成为事实源
- 新 session 应先读取哪些 scaffold artifacts，才能在 reset / worker replacement 后快速恢复定向
- Hive 如何并行协调 Planner、Research、Execution、Evaluator、Recovery 这些角色
- 运行中用户插话如何触发 impact analysis、preemption、replan、supersession
- context reset 如何从“一个命令”升级为完整恢复协议
- timeout、launch ambiguity、unknown live run、manual stop 下如何统一做终止与重派

## 明确不在当前阶段

- multi-writer distributed control plane
- multi-repo federation
- 复杂 policy engine
- rich UI / dashboard
- 完整人工审批工作流

## 建议阅读顺序

先看当前 MVP 控制平面：

1. [docs/README.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/README.md)
2. [01-Hive-Overall-Architecture.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/01-Hive-Overall-Architecture.md)
3. [02-Reference-Architecture.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/02-Reference-Architecture.md)
4. [03-MVP-Implementation-Blueprint.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/03-MVP-Implementation-Blueprint.md)
5. [04-Phased-Implementation-Plan.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/04-Phased-Implementation-Plan.md)
6. [07-MVP-Object-Package.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/03-state-model/07-MVP-Object-Package.md)
7. [11-Control-Plane-API-Contract.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/05-execution/11-Control-Plane-API-Contract.md)
8. [14-Command-Handler-Blueprint.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/05-execution/14-Command-Handler-Blueprint.md)

再看 vNext 长期自治多-agent harness：

1. [05-Hive-vNext-Long-Running-Agent-Harness.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/05-Hive-vNext-Long-Running-Agent-Harness.md)
2. [09-Input-to-Spec-and-TaskGraph-Pipeline.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/04-planning/09-Input-to-Spec-and-TaskGraph-Pipeline.md)
3. [10-Benchmark-Repo-Research-Protocol.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/04-planning/10-Benchmark-Repo-Research-Protocol.md)
4. [11-Project-Dossier-Compilation-Protocol.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/04-planning/11-Project-Dossier-Compilation-Protocol.md)
5. [08-vNext-Compiled-Artifact-Package.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/03-state-model/08-vNext-Compiled-Artifact-Package.md)
6. [12-Compilation-Lifecycle-and-Freshness-Protocol.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/04-planning/12-Compilation-Lifecycle-and-Freshness-Protocol.md)
7. [15-Agent-Role-Topology-and-Run-Contract.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/05-execution/15-Agent-Role-Topology-and-Run-Contract.md)
8. [16-Executor-Session-Scaffold-Profile.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/05-execution/16-Executor-Session-Scaffold-Profile.md)
9. [14-Context-Reset-and-Session-Handoff-Protocol.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/07-reliability/14-Context-Reset-and-Session-Handoff-Protocol.md)
10. [15-User-Interrupt-Replan-and-Preemption-Protocol.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/07-reliability/15-User-Interrupt-Replan-and-Preemption-Protocol.md)
11. [16-Run-Termination-and-Reassignment-Matrix.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/07-reliability/16-Run-Termination-and-Reassignment-Matrix.md)
12. [15-vNext-Compiled-Artifact-Schema-Catalog.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/08-appendix/15-vNext-Compiled-Artifact-Schema-Catalog.md)

详细目录、版本分层和路径兼容说明见 [docs/README.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/README.md)。
