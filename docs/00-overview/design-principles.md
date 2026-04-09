# Hive Design Laws

> 注：工程执行约束以 [engineering-laws.md](./engineering-laws.md) 为准；本文保留为早期原则摘要。

## Purpose

- 固化 Hive 的工程约束。
- 统一执行、恢复、验收的判断标准。

## Rules

### Law 1: Agents are disposable

- Worker 必须可替换。
- 单个 Worker 失败不得成为系统阻塞点。

### Law 2: State is external

- 项目状态必须写入外部对象。
- 对话和内存不是事实来源。

### Law 3: Tasks must be incremental

- Task 必须可拆分、可重复派发、可局部完成。
- 禁止用单个超大 Task 覆盖整段项目工作。

### Law 4: Every session reconstructs context

- 每次 Worker 启动必须重建上下文。
- 禁止依赖上一次 session 的隐式记忆继续执行。

### Law 5: Progress must be verifiable

- 任何进度都必须附带验证证据。
- 无证据的进度只能视为未完成。

### Law 6: No worker authority drift

- Worker 不得扩展自己的权限边界。
- Worker 不得自行修改需求、架构、Plan 或全局约束。

### Law 7: Deterministic state over agent memory

- 状态迁移必须显式记录。
- 系统连续性优先依赖状态对象，而不是 agent 记忆。

### Law 8: Recovery over conversation continuity

- 恢复能力优先于长对话连续性。
- 新 session 必须能仅依赖外部状态恢复工作。

## Anti-patterns

- 依赖单个长上下文 Worker 持续推进项目。
- 让关键状态只存在于一次对话中。
- 用“看起来做完了”代替验证与验收。
- 允许 Worker 越权修改架构、需求或 Plan。

## Acceptance Criteria

- 新协议文档不得违反上述 8 条。
- 新增 Task 规则必须体现增量执行、可验证、可恢复。
- 新增恢复规则必须假设 Worker 可丢弃、上下文可重建。
