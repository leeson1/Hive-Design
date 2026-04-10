# 12 Command and ChangeSet Examples

## Purpose

- 给出控制平面 command 与 change-set 的最小可执行示例。
- 为未来接口实现、测试夹具和回放工具提供样板。

## Scope

- 本文只提供 canonical examples。
- 具体 contract 以 `../05-execution/11-Control-Plane-API-Contract.md` 和 `../06-coordination/03-Change-Set-and-Outbox-Contract.md` 为准。

## Example 1: `submit_user_input(...)`

```yaml
command_name: submit_user_input
command_id: cmd_20260410_001
idempotency_key: input:user:20260410:001
payload:
  source: user
  content: 做一个带认证和权限模型的服务骨架
  conversation_ref: thread_main
  received_at: 2026-04-10T10:00:00Z
expected_events:
  - UserInputReceived
```

## Example 2: `prepare_dispatch(...)`

```yaml
command_name: prepare_dispatch
command_id: cmd_20260410_021
idempotency_key: dispatch:task_auth_backend_07:plan_rev_12
payload:
  task_id: task_auth_backend_07
  executor_profile_ref: profile_codex_default
  workspace_plan:
    workspace_ref: workspaces/run_codex_003
  lock_request_set:
    - scope_type: path
      mode: write
      resource_ref:
        repo: hive-service
        path_pattern: services/auth/**
expected_events:
  - DispatchPrepared
  - LockAcquired
```

## Example 3: Dispatch ChangeSet

```yaml
changeset_id: cs_20260410_0101
command_name: prepare_dispatch
command_id: cmd_20260410_021
idempotency_key: dispatch:task_auth_backend_07:plan_rev_12
object_deltas:
  - object_type: Task
    object_id: task_auth_backend_07
    before: {status: ready}
    after: {status: dispatching}
  - object_type: AgentRun
    object_id: run_codex_003
    before: null
    after:
      status: created
      task_id: task_auth_backend_07
lock_deltas:
  - lock_id: lock_auth_write_07
    before: {status: requested}
    after:
      status: reserved
      owner_task_id: task_auth_backend_07
      owner_run_id: run_codex_003
outbox_events:
  - event_id: evt_20260410_021
    event_type: DispatchPrepared
  - event_id: evt_20260410_022
    event_type: LockAcquired
commit_result:
  status: committed
```

## Example 4: Acceptance ChangeSet

```yaml
changeset_id: cs_20260410_0201
command_name: run_acceptance
command_id: cmd_20260410_031
idempotency_key: acceptance:handoff_20260410_03:policy_default
object_deltas:
  - object_type: Acceptance
    object_id: acceptance_20260410_01
    before: null
    after:
      status: accepted
      task_id: task_auth_backend_07
      handoff_id: handoff_20260410_03
  - object_type: Task
    object_id: task_auth_backend_07
    before: {status: awaiting_acceptance}
    after: {status: accepted}
outbox_events:
  - event_id: evt_20260410_031
    event_type: AcceptancePassed
commit_result:
  status: committed
```

## Example 5: `start_recovery(...)`

```yaml
command_name: start_recovery
command_id: cmd_20260410_041
idempotency_key: recovery:run_codex_003:timeout
payload:
  recovery_reason: agent_run_timeout
  related_object_refs:
    - object_type: AgentRun
      object_id: run_codex_003
    - object_type: Lock
      object_id: lock_auth_write_07
  latest_checkpoint_id: checkpoint_20260410_01
expected_events:
  - RecoveryStarted
  - LockRecoveryHeld
```

## Anti-patterns

- 示例里使用非 canonical 前缀。
- command 示例与 change-set 示例的事件名对不上。
- acceptance 示例继续使用 `needs-followup` 这类 legacy form。

## Acceptance Criteria

- 示例可直接作为接口测试 fixture 的起点。
- 示例里的命名、字段和事件与 canonical registry 一致。
