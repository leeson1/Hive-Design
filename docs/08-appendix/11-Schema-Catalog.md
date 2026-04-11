# 11 Schema Catalog

## Purpose

- 提供统一的 canonical schema catalog。
- 为实现方提供对象、事件、command carrier 的最小字段目录。
- 统一 required / optional / enum / identifier 信息。

## Scope

- 本文是 schema catalog，不是数据库 DDL。
- 具体枚举与命名规则以 `../03-state-model/06-Canonical-Enums-and-Identifiers.md` 为准。
- vNext durable compiled artifacts 与 pointer extension 的最小 schema 见 `15-vNext-Compiled-Artifact-Schema-Catalog.md`。

## Schema Format

所有 schema 统一使用以下格式：

```yaml
ObjectName:
  id_field: object_id
  required: {}
  optional: {}
  enums: {}
```

## Directive

```yaml
Directive:
  id_field: directive_id
  required:
    directive_id: string
    status: string
    source: string
    content: string
    created_at: datetime
  optional:
    impact_scope: object
    decision: string
    superseded_by_directive_id: string
    evidence_pack_refs: array
    research_artifact_refs: array
  enums:
    status: [created, assessing, applied, escalated, superseded, archived]
```

## PlanRevision

```yaml
PlanRevision:
  id_field: plan_revision_id
  required:
    plan_revision_id: string
    execution_plan_id: string
    status: string
    previous_revision_id: string|null
    created_at: datetime
  optional:
    directive_refs: array
    phase_ids: array
    superseded_task_ids: array
    new_task_ids: array
    product_spec_ref: string
    execution_package_ref: string
    task_graph_ref: string
    active_dossier_ref: string
  enums:
    status: [draft, compiled, active, superseded, archived]
```

## Phase

```yaml
Phase:
  id_field: phase_id
  required:
    phase_id: string
    plan_revision_id: string
    status: string
    title: string
  optional:
    acceptance_criteria: array
    validation_plan: array
    blocker_issue_ids: array
  enums:
    status: [draft, active, blocked, completed, cancelled, superseded, archived]
```

## Task

```yaml
Task:
  id_field: task_id
  required:
    task_id: string
    phase_id: string
    plan_revision_id: string
    status: string
    objective: string
    scope: object
    constraints: array
    done_criteria: array
    validation_method: array
  optional:
    allowed_paths: array
    forbidden_paths: array
    dependencies: array
    blockers: array
    path_locks: object
    output_expectations: array
    escalation_rule: string
  enums:
    status: [draft, ready, dispatching, dispatched, awaiting_acceptance, accepted, requeued, blocked, cancelled, superseded, archived]
```

## AgentRun

```yaml
AgentRun:
  id_field: run_id
  required:
    run_id: string
    task_id: string
    executor_name: string
    status: string
    workspace_ref: string
    lease_expires_at: datetime
  optional:
    last_heartbeat_at: datetime
    start_sla_expires_at: datetime
    exit_status: string
    handoff_ref: string
    log_refs: array
    adapter_run_ref: string
  enums:
    status: [created, starting, running, exited, start_failed, timed_out, killed, archived]
    exit_status: [succeeded, failed, blocked, timed_out, cancelled, killed, unknown]
```

## Handoff

```yaml
Handoff:
  id_field: handoff_id
  required:
    handoff_id: string
    task_id: string
    run_id: string
    status: string
    result_claim: string
    artifact_refs: array
  optional:
    modified_files: array
    validation_results: object
    decisions_made: array
    assumptions: array
    risks: array
    remaining_issues: array
    next_steps: array
  enums:
    status: [draft, submitted, ingested, linked_to_acceptance, archived]
    result_claim: [complete, partial, failed, blocked]
```

## Acceptance

```yaml
Acceptance:
  id_field: acceptance_id
  required:
    acceptance_id: string
    task_id: string
    handoff_id: string
    status: string
    reason: string
  optional:
    run_id: string
    input_set: object
    evidence_summary: object
    followup_actions: array
  enums:
    status: [pending, accepted, rejected, needs_followup, partial_accepted, archived]
```

## Issue

```yaml
Issue:
  id_field: issue_id
  required:
    issue_id: string
    type: string
    status: string
    source_object_ref: string
    impact: string
  optional:
    evidence_refs: array
    suggested_actions: array
    escalation_path: string
  enums:
    type: [execution_failure, design_conflict, requirement_conflict, lock_conflict, recovery_anomaly]
    status: [open, triaged, escalated, resolved, archived]
```

## Lock

```yaml
Lock:
  id_field: lock_id
  required:
    lock_id: string
    scope_type: string
    mode: string
    status: string
    resource_ref: object
  optional:
    owner_task_id: string
    owner_run_id: string
    lease_expires_at: datetime
    last_renewed_at: datetime
    recovery_hold_until: datetime
    conflict_with: array
  enums:
    scope_type: [repo, module, path]
    mode: [read, write]
    status: [requested, reserved, active, recovery_hold, released, force_released, expired]
```

## Checkpoint

```yaml
Checkpoint:
  id_field: checkpoint_id
  required:
    checkpoint_id: string
    status: string
    created_at: datetime
    plan_revision_id: string
    event_log_cursor: string
  optional:
    active_phase_id: string
    active_directive_ids: array
    open_task_ids: array
    active_run_ids: array
    active_lock_ids: array
    open_issue_ids: array
    pending_decision_ids: array
    active_artifact_refs: array
  enums:
    status: [written, superseded, archived]
```

## Event

```yaml
Event:
  id_field: event_id
  required:
    event_id: string
    event_type: string
    object_ref: object
    producer: object
    occurred_at: datetime
    idempotency_key: string
  optional:
    payload: object
    caused_by_event_id: string
    correlation_id: string
  enums:
    event_type:
      - UserInputReceived
      - RuntimeDirectiveCreated
      - ResearchRequested
      - ResearchSprintCompiled
      - EvidencePackCompiled
      - ProductSpecCompiled
      - ExecutionPackageCompiled
      - PlanCompiled
      - PlanRevised
      - TaskCreated
      - TaskQualified
      - TaskGraphCompiled
      - DispatchPrepared
      - RunContractCompiled
      - SessionScaffoldCompiled
      - TaskDispatched
      - TaskRequeued
      - TaskBlocked
      - TaskSuperseded
      - TaskCancelled
      - AgentRunStarted
      - AgentRunHeartbeatReported
      - AgentRunHeartbeatMissed
      - AgentRunStartFailed
      - AgentRunTimedOut
      - AgentRunKilled
      - AgentRunExited
      - HandoffSubmitted
      - AcceptancePassed
      - AcceptanceRejected
      - AcceptanceNeedsFollowup
      - AcceptancePartiallyAccepted
      - IssueOpened
      - IssueEscalated
      - LockAcquired
      - LockConflictDetected
      - LockRecoveryHeld
      - LockReleased
      - ProjectDossierCompiled
      - CheckpointWritten
      - ContextResetRequested
      - RecoveryStarted
      - RecoveryCompleted
```

## ChangeSet

```yaml
ChangeSet:
  id_field: changeset_id
  required:
    changeset_id: string
    command_name: string
    command_id: string
    idempotency_key: string
    issued_at: datetime
    actor_ref: string
    object_deltas: array
    outbox_events: array
    commit_result: object
  optional:
    lock_deltas: array
    external_side_effects: array
    reconciliation_markers: array
    retry_markers: array
    compensation_markers: array
    correlation_id: string
  enums:
    commit_result.status: [committed, rejected, partially_applied]
```

## DispatchIntent

```yaml
DispatchIntent:
  id_field: dispatch_intent_id
  required:
    dispatch_intent_id: string
    task_id: string
    run_id: string
    executor_name: string
    workspace_ref: string
    status: string
  optional:
    lock_request_set: array
    capability_profile_ref: string
    side_effect_token_id: string
    run_contract_ref: string
    session_scaffold_ref: string
  enums:
    status: [prepared, launched, superseded, cancelled]
```

## RecoveryAction

```yaml
RecoveryAction:
  id_field: recovery_action_id
  required:
    recovery_action_id: string
    reason: string
    status: string
    related_object_refs: array
  optional:
    latest_checkpoint_id: string
    proposed_action: string
    resulting_task_id: string
  enums:
    status: [planned, running, completed, cancelled]
```

## Anti-patterns

- schema 目录和 canonical enums 目录互相矛盾。
- required / optional 未区分，导致实现方只能猜。
- event_type 在不同文件里出现不同拼写。

## Acceptance Criteria

- 实现方能从本文直接生成 validator、type definition 或 schema stub。
- 所有核心对象、事件、change-set carrier 都有统一格式。
- required / optional / enum 字段已明确分离。
