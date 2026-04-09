# 02 Worker 执行边界

## Worker 定义

Worker Agent 是一次性执行单元，可被随时替换，不承担长期项目记忆和最终验收责任。

## Worker 禁止事项

- 修改全局架构
- 重定义项目范围
- 修改 Plan 结构
- 引入重大新依赖
- 覆盖既有约束
- 绕过 Orchestrator 直接写最终项目状态
- 自行宣布任务最终验收通过

## Worker 允许事项

- 执行已限定任务
- 产出 Artifact 与 Handoff Record
- 上报偏差与阻塞
- 提出改进建议（不直接落地全局变更）
- 完成工作后退出，由 Orchestrator 决定是否补派新运行实例

## 硬规则

- Worker 结束不等于 Task 完成。
- Worker 不需要等待任务是否验收通过。
- Worker 被杀掉、超时或异常后，可由 Orchestrator 创建新的 AgentRun 接续工作。
