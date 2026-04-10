# 08 对象 Schema 草案

## Purpose

- 给出关键对象的最小落库字段草案。
- 让实现方可以据此设计文件对象或数据库记录。

## Scope

- 以下 schema 是 v1 最小建议，不是最终数据库设计。
- 字段可扩展，但核心语义不应漂移。

## Directive

```yaml
directive_id: dir_001
source: user
status: applied
created_at: 2026-04-10T10:00:00Z
content: 优先做认证模块，暂停移动端界面
impact_scope:
  plan_revision_ids:
    - plan_rev_12
  task_ids:
    - task_mobile_ui_01
decision: supersede
```

## Execution Plan Revision

```yaml
execution_plan_id: plan_main
plan_revision_id: plan_rev_12
previous_revision_id: plan_rev_11
status: active
phase_ids:
  - phase_auth
directive_refs:
  - dir_001
```

## Task

```yaml
task_id: task_auth_backend_07
phase_id: phase_auth
plan_revision_id: plan_rev_12
status: ready
objective: 完成认证服务基础实现
scope:
  include:
    - auth service
constraints:
  - no architecture change
allowed_paths:
  - services/auth/**
forbidden_paths:
  - mobile/**
done_criteria:
  - tests pass
validation_method:
  - unit tests
dependencies:
  - task_auth_schema_01
```

## AgentRun

```yaml
run_id: run_codex_003
task_id: task_auth_backend_07
executor_name: codex
status: running
workspace_ref: workspaces/run_codex_003
lease:
  lease_expires_at: 2026-04-10T12:30:00Z
  last_heartbeat_at: 2026-04-10T12:05:00Z
exit_status: null
handoff_ref: null
```

## Handoff

```yaml
handoff_id: handoff_003
task_id: task_auth_backend_07
run_id: run_codex_003
result_claim: partial
artifact_refs:
  - artifact_logs_003
validation_results:
  tests: failed
risks:
  - integration missing
remaining_issues:
  - issue_auth_timeout_01
```

## Acceptance

```yaml
acceptance_id: acc_001
task_id: task_auth_backend_07
handoff_id: handoff_003
result: needs-followup
reason: integration evidence missing
followup_actions:
  - create_task_auth_integration_09
```

## Issue

```yaml
issue_id: issue_auth_timeout_01
type: execution_failure
source_object_ref: run_codex_003
status: open
impact: auth phase blocked
suggested_actions:
  - reassign
  - restore_if_supported
```

## Checkpoint

```yaml
checkpoint_id: cp_20260410_01
created_at: 2026-04-10T12:40:00Z
plan_revision_id: plan_rev_12
active_phase_id: phase_auth
open_task_ids:
  - task_auth_backend_07
active_run_ids: []
open_issue_ids:
  - issue_auth_timeout_01
```

## Event

```yaml
event_id: evt_001
event_type: AgentRunTimedOut
object_ref:
  object_type: AgentRun
  object_id: run_codex_003
producer:
  role: LeaseMonitor
occurred_at: 2026-04-10T12:35:00Z
idempotency_key: run_codex_003:timeout
```
