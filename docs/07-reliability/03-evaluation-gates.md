# 03 Evaluation Gates

## Purpose

- 定义 Hive 的验证闸门。
- 保证 Task completion 和 Phase progression 都依赖验证结果。

## Rules

### Evaluation Rule

- Task completion requires validation.
- 未通过 validation 的 Task 不得进入 completed 语义。
- Orchestrator 不得推进 Phase，除非 evaluation 通过。

### Validation Types

- code validation
- test validation
- requirement validation
- integration validation

规则：

- Validation 类型由 Task spec 明确指定。
- 至少要覆盖 done criteria 和 output expectations。
- 无法执行的验证项必须显式记录原因与影响。

### Evidence Rule

- 每个 validation 必须有证据。
- 证据可以是日志、测试报告、构建结果、diff、artifact 引用。

### No Silent Progress Rule

- No silent progress.
- 任何进度必须可验证。
- 无验证证据的进度只能视为 in-progress 或 pending。

## Anti-patterns

- 仅凭 Worker 总结就推进 Task。
- 未做集成验证就宣称整合完成。
- 验证失败但不写入状态或 Issue。
- 用“人工感觉没问题”代替证据。

## Acceptance Criteria

- 每个完成的 Task 都必须关联 validation evidence。
- 每次 Phase 推进都必须能回溯到 evaluation pass。
- 无证据的进度不得进入完成态。
