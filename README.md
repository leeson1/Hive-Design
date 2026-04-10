# Hive Design

Hive 是一个围绕多执行器工作流的控制平面设计仓。当前文档版本是 `MVP Implementation Package Draft v0.6`。

本仓库只包含设计文档，不是首个实现仓，也不包含业务代码实现。当前目标是把已有协议收敛成“第一个 Hive 控制平面原型仓该如何搭建”，让工程师可以按文档开始实现单 writer、单仓库、单 adapter 的 MVP 闭环。

最短阅读入口：

1. [docs/README.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/README.md)
2. [03-MVP-Implementation-Blueprint.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/03-MVP-Implementation-Blueprint.md)
3. [04-Phased-Implementation-Plan.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/00-overview/04-Phased-Implementation-Plan.md)
4. [07-MVP-Object-Package.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/03-state-model/07-MVP-Object-Package.md)
5. [14-Command-Handler-Blueprint.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/05-execution/14-Command-Handler-Blueprint.md)
6. [09-End-to-End-Sequence-Scenarios.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/07-reliability/09-End-to-End-Sequence-Scenarios.md)
7. [04-MVP-Storage-Backend-Profile.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/06-coordination/04-MVP-Storage-Backend-Profile.md)

如果你只想先看当前阶段结论：

- Hive 是控制平面，不是通用 agent。
- authoritative object state 仍是当前事实来源。
- Event Log 是历史与重放输入，不是当前事实源。
- Checkpoint 是恢复快照，不是事实源。
- MVP 首版推荐 `SQLite + filesystem`。
- MVP 首适配器推荐 `Codex`，但恢复、心跳、验收、锁与 recovery 仍由 host-side Orchestrator 兜底。
- 当前重点是 first implementation 可直接开工的实现前设计包：蓝图、对象包、handler 映射、黄金路径和分阶段实施计划。

详细目录、阅读顺序和版本说明见 [docs/README.md](/Users/leeson/codes/docker_workspace/Hive-Design/docs/README.md)。
