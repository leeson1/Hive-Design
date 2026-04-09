# 03 Handoff 记录规范

## 定位

Handoff 是 Worker 退出前提交给 Orchestrator 的结构化交接包，不是最终项目真相。

## 提交流向

`Worker -> Handoff Record / Artifact -> Orchestrator -> Acceptance -> 状态更新`

## 交接与验收时序图

```mermaid
sequenceDiagram
    participant W as Worker Agent
    participant O as Orchestrator
    participant S as State Store

    W->>O: 提交 Handoff Record
    W->>S: 写入 Artifact / 日志引用
    W-->>O: 退出

    O->>S: 读取 Task done criteria
    O->>S: 读取 validation results / artifacts
    O->>O: 验收判断

    alt 验收通过
        O->>S: 写入 Acceptance Record(result=Accepted)
        O->>S: 更新 Task / Phase / Checkpoint
    else 需要重派
        O->>S: 写入 Acceptance Record(result=Rejected or NeedsFollowup)
        O->>S: 更新 Task 为 Requeued / Blocked
        O->>O: 生成后续 Task 或新的 AgentRun
    end
```

## 必填字段

- task_id
- run_id
- objective_echo
- self_report_result
- files_modified
- artifact_refs
- summary
- deviations_from_plan
- assumptions_made
- validation_results
- unresolved_questions
- suggested_next_steps

## 目的

- 防止“静默偏航”
- 保障接力可读性
- 支持审计与回滚

## Orchestrator 验收动作

- 校验 done criteria 与 validation_results
- 判断任务进入 Accepted、Requeued、Blocked 或 Cancelled
- 必要时生成新的 Task、Issue 或 Decision
- 更新 Task、AgentRun、Checkpoint 等相关状态
