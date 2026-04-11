# 15 vNext Compiled Artifact Schema Catalog

## Purpose

- 为 vNext durable compiled artifacts 提供最小 schema catalog。
- 让实现方在进入下一阶段时，可以直接据此生成 validator、type definitions 或 storage metadata。
- 补齐 `11-Schema-Catalog.md` 尚未覆盖的 artifact-level schemas。

## Scope

- 本文只覆盖 compiled artifact metadata 和典型 payload linkage，不是最终 DDL。
- MVP core runtime objects 仍以 `11-Schema-Catalog.md` 为准。
- artifact package 语义见 `../03-state-model/08-vNext-Compiled-Artifact-Package.md`。

## Artifact Status Enum

```yaml
ArtifactStatus:
  enum: [compiled, active, superseded, stale, failed, archived]
```

## CompilationBatch

```yaml
CompilationBatch:
  id_field: compilation_batch_id
  required:
    compilation_batch_id: string
    trigger_ref: string
    target_plan_revision_id: string
    status: string
    compiled_at: datetime
  optional:
    input_refs: array
    output_refs: array
    failure_reason: string
  enums:
    status: [compiled, partial, failed, archived]
```

## ResearchSprintArtifact

```yaml
ResearchSprintArtifact:
  id_field: research_sprint_id
  required:
    research_sprint_id: string
    status: string
    objective: string
    questions: array
    compiled_at: datetime
  optional:
    source_budget: object
    allowed_sources: array
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, superseded, archived]
```

## EvidencePackArtifact

```yaml
EvidencePackArtifact:
  id_field: evidence_pack_id
  required:
    evidence_pack_id: string
    status: string
    compiled_at: datetime
    compiled_from_refs: array
  optional:
    claims: array
    options: array
    risks: array
    open_questions: array
    validation_candidates: array
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## ProductSpecArtifact

```yaml
ProductSpecArtifact:
  id_field: product_spec_id
  required:
    product_spec_id: string
    status: string
    compiled_at: datetime
    source_directive_refs: array
  optional:
    evidence_pack_refs: array
    objective: string
    scope_include: array
    scope_exclude: array
    invariants: array
    success_criteria: array
    accepted_assumptions: array
    unresolved_questions: array
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## ExecutionPackageArtifact

```yaml
ExecutionPackageArtifact:
  id_field: execution_package_id
  required:
    execution_package_id: string
    status: string
    compiled_at: datetime
    product_spec_ref: string
    plan_revision_id: string
  optional:
    worklines: array
    milestones: array
    replan_hooks: array
    requirement_ledger_ref: string
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## TaskGraphArtifact

```yaml
TaskGraphArtifact:
  id_field: task_graph_id
  required:
    task_graph_id: string
    status: string
    compiled_at: datetime
    plan_revision_id: string
    execution_package_ref: string
  optional:
    task_node_refs: array
    dependency_edges: array
    conflict_edges: array
    ready_set_summary: object
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## RunContractArtifact

```yaml
RunContractArtifact:
  id_field: run_contract_id
  required:
    run_contract_id: string
    status: string
    compiled_at: datetime
    role: string
    task_ref: string
  optional:
    plan_revision_id: string
    task_graph_ref: string
    evidence_refs: array
    file_path_scope: object
    constraints: array
    done_criteria: array
    validation_method: array
    escalation_rule: array
    timeout_heartbeat_expectation: object
    handoff_requirements: array
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## ProjectDossierArtifact

```yaml
ProjectDossierArtifact:
  id_field: dossier_id
  required:
    dossier_id: string
    status: string
    compiled_at: datetime
    plan_revision_id: string
  optional:
    requirement_ledger_ref: string
    latest_checkpoint_ref: string
    latest_handoff_summary_ref: string
    section_index: object
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## SessionScaffoldArtifact

```yaml
SessionScaffoldArtifact:
  id_field: scaffold_id
  required:
    scaffold_id: string
    status: string
    compiled_at: datetime
    run_contract_ref: string
  optional:
    requirement_feature_coverage_view_ref: string
    recent_progress_digest_ref: string
    workspace_bootstrap_entry_ref: string
    baseline_smoke_check_contract_ref: string
    read_first_manifest_ref: string
    checkpoint_ref: string
    latest_handoff_ref: string
    plan_revision_id: string
    task_spec_ref: string
    payload_ref: string
    compilation_batch_id: string
    superseded_by_ref: string
  enums:
    status: [compiled, active, superseded, stale, archived]
```

## Pointer Carrier Extension

```yaml
PlanRevisionExtension:
  optional:
    product_spec_ref: string
    execution_package_ref: string
    task_graph_ref: string
    active_dossier_ref: string

DispatchIntentExtension:
  optional:
    run_contract_ref: string
    session_scaffold_ref: string

DirectiveExtension:
  optional:
    evidence_pack_refs: array
    research_artifact_refs: array
```

## Anti-patterns

- 把 compiled artifacts 的完整正文强塞进 core runtime object 表，导致对象边界膨胀。
- 没有 `compilation_batch_id`，无法追踪哪轮编译生成了哪些 outputs。
- 给 artifact schema 定义一堆 runtime state 字段，和 authoritative object tables 混层。

## Acceptance Criteria

- 实现方能根据本文为 compiled artifacts 建立 validator 和 metadata storage。
- 读者能区分 runtime objects schema 与 compiled artifact schema。
- pointer carrier 扩展与 artifact schema 之间的关系明确。
