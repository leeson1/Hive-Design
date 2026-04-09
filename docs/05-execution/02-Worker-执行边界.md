# 02 Worker 执行边界

## Purpose

- 固定 Worker 的权限边界。
- 保证 Worker 可替换而不漂移为治理角色。

## Rules

### Worker Definition

- Worker Agent 是一次性执行单元。
- Worker 不承担长期项目记忆。
- Worker 不承担最终验收责任。

### Worker Prohibitions

- 修改全局架构
- 重定义项目范围
- 修改 Plan 结构
- 引入重大新依赖
- 覆盖既有约束
- 绕过 Orchestrator 直接写最终项目状态
- 自行宣布任务最终验收通过

### Worker Permissions

- 执行已限定任务
- 产出 Artifact 与 Handoff Record
- 上报偏差与阻塞
- 提出改进建议
- 完成工作后退出

### Hard Rules

- Worker 结束不等于 Task 完成。
- Worker 不需要等待任务是否验收通过。
- Worker 被杀掉、超时或异常后，可由 Orchestrator 创建新的 AgentRun 接续工作。

## Anti-patterns

- Worker 顺手修改 scope 外模块。
- Worker 看到问题后直接改 Plan 或 Requirement。
- Worker 以“已经做完”为由跳过验收流程。
- Worker 失败后要求保留隐式上下文继续工作。

## Acceptance Criteria

- Worker 的输入必须受 Task scope 和 constraints 限制。
- Worker 的输出必须是 Artifact、Handoff 或显式阻塞记录。
- Worker 的任何结束都不得直接写成最终 Task completion。
