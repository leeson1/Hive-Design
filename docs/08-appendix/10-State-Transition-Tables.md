# 10 State Transition Tables

## Purpose

- 将关键对象的状态迁移规则收敛为可检索表格。
- 为实现方提供明确的 trigger、guard、side effect 和 emitted event 基线。

## Scope

- 本文是状态迁移总表，不替代正文协议。
- 若正文与表格冲突，以正文协议修订为准，并应同步更新本表。

## Directive

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `created` | input normalized | raw input accepted | `assessing` | impact analysis started | `RuntimeDirectiveCreated` |
| `assessing` | impact resolved | affected scope identified | `applied` | write decision / plan action | `PlanRevised` or `TaskCreated` or `IssueOpened` |
| `assessing` | requirement conflict | needs high-order decision | `escalated` | open decision / queen escalation | `IssueEscalated` |
| `applied` | newer directive supersedes | same workline replaced | `superseded` | checkpoint delta | `CheckpointWritten` |
| `applied` | workline closed | no further routing needed | `archived` | archive refs | none |

## Execution Plan Revision

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `draft` | compilation complete | brief / evidence available | `compiled` | store revision draft | `PlanCompiled` |
| `compiled` | activation approved | charter constraints satisfied | `active` | previous active revision superseded | `PlanRevised` |
| `active` | newer revision activated | replacement exists | `superseded` | affected tasks evaluated | `TaskCreated` / `IssueOpened` |
| `superseded` | archive policy | references preserved | `archived` | archive metadata | none |

## Task

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `draft` | qualification passed | required fields complete | `ready` | ready queue candidate | `TaskQualified` |
| `ready` | dispatch prepared | deps satisfied, no blocker, lock reservable | `dispatching` | create AgentRun(created), reserve lock | `DispatchPrepared` |
| `dispatching` | launch acknowledged | adapter confirms start | `dispatched` | AgentRun running, lock active | `TaskDispatched`, `AgentRunStarted`, `LockAcquired` |
| `dispatching` | launch failed / start SLA exceeded | no live run found | `requeued` | AgentRun start_failed, lock released | `AgentRunStartFailed`, `LockReleased` |
| `dispatched` | handoff submitted | run exited | `awaiting_acceptance` | handoff stored | `HandoffSubmitted` |
| `awaiting_acceptance` | acceptance pass | evidence complete | `accepted` | phase progress updated | `AcceptancePassed` |
| `awaiting_acceptance` | acceptance reject | evidence invalid / missing | `requeued` or `blocked` | issue / followup created | `AcceptanceRejected` |
| `ready` or `dispatching` or `dispatched` | directive supersedes | replacement revision active | `superseded` | linked replacement task | `PlanRevised` |
| `ready` or `dispatching` | cancel approved | workline cancelled | `cancelled` | release locks / close run path | `IssueOpened` or `CheckpointWritten` |

## AgentRun

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `created` | adapter launch started | dispatch committed | `starting` | start SLA begins | `DispatchPrepared` |
| `starting` | adapter ack | launch confirmed | `running` | heartbeat expected | `AgentRunStarted` |
| `starting` | launch fail / no ack | start SLA exceeded | `start_failed` | task requeue eligible | `AgentRunStartFailed` |
| `running` | process exit | normal end | `exited` | handoff intake path | `AgentRunExited` |
| `running` | missed heartbeat beyond lease | no recovery yet | `timed_out` | recovery started | `AgentRunTimedOut`, `RecoveryStarted` |
| `running` | kill requested | hard kill executed | `killed` | recovery hold on locks | `AgentRunKilled` |

## Handoff

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `draft` | worker submits | required fields present | `submitted` | artifact refs persisted | `HandoffSubmitted` |
| `submitted` | acceptance intake | task / run refs valid | `ingested` | acceptance input set built | none |
| `ingested` | acceptance finished | acceptance recorded | `linked_to_acceptance` | archive candidate | `AcceptancePassed` or `AcceptanceRejected` or `AcceptanceNeedsFollowup` |
| `linked_to_acceptance` | archive policy | refs stable | `archived` | archive metadata | none |

## Acceptance

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `pending` | evidence passes | done criteria met | `accepted` | task accepted | `AcceptancePassed` |
| `pending` | evidence fails | invalid or missing evidence | `rejected` | task requeued / blocked | `AcceptanceRejected` |
| `pending` | evidence partial | useful artifact remains | `partial_accepted` | followup action required | `AcceptancePartiallyAccepted` |
| `pending` | more work required | followup task needed | `needs_followup` | create task / issue | `AcceptanceNeedsFollowup` |
| `accepted` or `rejected` or `partial_accepted` or `needs_followup` | archive policy | refs stable | `archived` | archive metadata | none |

## Issue

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `open` | triage completed | owner assigned | `triaged` | recovery or decision path selected | `IssueOpened` |
| `triaged` | escalation needed | requirement / design conflict | `escalated` | queen or decision routing | `IssueEscalated` |
| `triaged` or `escalated` | resolution applied | guard satisfied | `resolved` | unblock task / phase | `RecoveryCompleted` or `CheckpointWritten` |
| `resolved` | archive policy | no open refs | `archived` | archive metadata | none |

## Lock

| Current State | Trigger | Guard Condition | Next State | Side Effects | Emitted Events |
|---|---|---|---|---|---|
| `requested` | grant | no conflict | `reserved` | dispatch may proceed | `LockAcquired` |
| `reserved` | run start ack | AgentRun running | `active` | owner bound | `LockAcquired` |
| `reserved` | launch fail | no active run | `released` | allow reschedule | `LockReleased` |
| `active` | normal completion | artifacts persisted | `released` | remove lock ownership | `LockReleased` |
| `active` | run timeout / kill | owner unstable | `recovery_hold` | block conflicting writes | `LockRecoveryHeld` |
| `recovery_hold` | hold TTL exceeded | no live run, no pending artifact intake | `force_released` | open audit issue if needed | `LockReleased`, `IssueOpened` |
| `active` | lease expired without renewal | stale confirmed | `expired` | recovery required | `IssueOpened` |

## Anti-patterns

- 同一对象状态机在不同章节使用不同枚举而不统一。
- trigger 只有自然语言描述，没有 emitted event。
- side effects 写成“系统处理”，没有对象级动作。

## Acceptance Criteria

- 实现方能从表格直接推导对象状态迁移。
- 每个关键对象至少能找到 trigger、guard、next state、side effects、emitted events。
- 表格与正文协议保持一致，可作为后续实现核对表。
