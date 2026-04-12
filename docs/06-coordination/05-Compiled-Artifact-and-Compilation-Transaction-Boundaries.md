# 05 Compiled Artifact 与 Compilation Transaction Boundaries

## Purpose

- 把 compiled artifact 的 metadata row / payload root / artifact ref URI / 目录布局收口为可实现规范。
- 明确 compilation batch、change-set、outbox、pointer switch 的事务边界。
- 保证 artifact durable 化后仍然服从现有 truth hierarchy 和 single-writer 提交模型。

## Scope

- 本文覆盖 vNext compiled artifact 的 durable layout 与 compilation change-set 协议。
- 本文不改变 `PlanRevision`、`Task`、`DispatchIntent`、`AgentRun` 的 authoritative 地位。
- 具体 freshness 规则见 `../04-planning/12-Compilation-Lifecycle-and-Freshness-Protocol.md`。
- schema catalog 见 `../08-appendix/15-vNext-Compiled-Artifact-Schema-Catalog.md`。

## Definitions

- `Artifact Metadata Row`：存放在 SQLite 的结构化记录，用于索引、lineage、freshness、pointer 切换与 supersession。
- `Artifact Payload Root`：artifact payload 在 filesystem 中的根目录。
- `Artifact Ref URI`：稳定指向 artifact payload 或 payload 子项的 URI。
- `Compilation Prepare ChangeSet`：记录 batch、metadata row、pending pointer plan 的事务。
- `Compilation Activate ChangeSet`：在 payload durable 后切换 active pointers、写 supersession 和 outbox 的事务。
- `Non-Canonical Output`：编译中间产物或失败产物，可保留调试，但不得成为 active pointer 目标。

## Rules

### Durable Storage Rule

compiled artifact 必须采用 `metadata row + payload` 分离模型：

- metadata row 存于 SQLite
- payload 存于 filesystem artifact root

不得只写 payload 文件而无 metadata row。

### Artifact Metadata Row Minimum Fields

每个 artifact metadata row 至少必须包含：

- `artifact_id`
- `artifact_type`
- `status`
- `compilation_batch_id`
- `compiled_at`
- `compiled_from_refs`
- `payload_root_uri`
- `payload_entry_uri`
- `payload_format`
- `payload_digest`
- `plan_revision_id` 或 `dispatch_intent_id`
- `canonical_pointer_scope`
- `superseded_by_ref`
- `is_embedded_payload`

规则：

- `payload_root_uri` 指向该 artifact 的 payload 根。
- `payload_entry_uri` 指向默认读取入口，例如 `artifact.yaml` 或 `manifest.json`。
- `canonical_pointer_scope` 只允许取：
  - `directive`
  - `plan_revision`
  - `dispatch_intent`
  - `checkpoint_summary`
- 若 payload 内嵌在 metadata row，`is_embedded_payload=true`，但仍必须保留 `payload_format`、`payload_digest`。

### Artifact Ref URI Rule

artifact ref URI 统一使用以下格式：

```text
artifact://<artifact_type>/<artifact_id>
artifact://<artifact_type>/<artifact_id>#<entry_relpath>
```

示例：

```text
artifact://product_spec/spec_20260412_01
artifact://task_graph/tg_20260412_01#graph/task-nodes.json
artifact://session_scaffold/scaffold_20260412_03#read-first-manifest.yaml
```

规则：

- 不使用 runtime object id 直接代替 artifact URI。
- URI 只代表 compiled artifact durable 引用，不代表 authoritative object state。
- payload root 下的子文件引用必须使用 `#<entry_relpath>`。

### Payload Root and Directory Layout Rule

filesystem 推荐目录布局如下：

```text
artifacts/
  compiled/
    <artifact_type>/
      <artifact_id>/
        metadata.snapshot.json
        artifact.<json|yaml|md>
        manifest.json
        refs/
        graph/
        evidence/
        scaffold/
```

最小约束：

- 每个 artifact 必须独占一个目录。
- 目录名必须等于 `artifact_id`。
- `metadata.snapshot.json` 是冗余快照，便于脱机调试；不是 authoritative metadata row。
- `manifest.json` 必须列出 payload 内部可引用 entry。
- 默认入口文件应固定为：
  - 结构化 artifact：`artifact.yaml` 或 `artifact.json`
  - dossier：`artifact.md`

### Embedded Payload Rule

仅以下条件可允许小 payload 内嵌：

- payload 小于实现方定义的 `small_payload_threshold`
- payload 不包含图结构、分段 evidence、read-first 清单等多文件内容
- 不影响调试和审计

即使内嵌，也必须：

- 保留 `payload_digest`
- 保留逻辑上的 `payload_entry_uri`
- 允许后续迁移到文件化 payload 而不改上层引用语义

### Compilation Transaction Boundary Rule

一次 canonical artifact 编译必须拆成两个边界：

1. `prepare` 边界
   - 写 `CompilationBatch`
   - 写 artifact metadata row，状态为 `compiled_pending_activation` 或 `failed`
   - 写 reconciliation / retry marker
2. `activate` 边界
   - 在确认 payload durable 后
   - 更新 active pointers
   - 标记旧 artifact `superseded`
   - 写 outbox events

规则：

- payload 文件写入不要求与 SQLite 同事务，但必须先 durable，再允许 activate。
- active pointer 切换不得与 payload 未落盘状态同时出现。
- pointer switch 与 supersession mapping 必须在同一 activate change-set 内完成。

### Compilation Batch 与 Change-Set 边界

对于一次 compile，推荐最小 change-set 序列：

1. `prepare_compilation_batch`
   - 创建 `CompilationBatch(status=preparing)`
   - 记录 `input_refs`
2. `record_compiled_artifact`
   - 为每个输出 artifact 写 metadata row
   - 若 payload 尚未 durable，则状态为 `compiled_pending_activation`
3. `activate_compiled_artifacts`
   - 切换 `PlanRevision` / `DispatchIntent` pointers
   - 更新旧 artifact 为 `superseded`
   - `CompilationBatch -> compiled`
   - 写 `CompiledArtifactActivated` outbox events

若某层失败：

- `CompilationBatch.status=failed` 或 `partial`
- 失败层及其下游不得进入 activate change-set

### Outbox Boundary Rule

下列内容必须进入 `activate_compiled_artifacts` change-set：

- pointer 更新
- supersession mapping
- `CompilationBatch.status` 最终状态
- outbox events：
  - `CompiledArtifactPrepared`
  - `CompiledArtifactActivated`
  - `CompiledArtifactSuperseded`

下列内容不得阻塞 activate：

- dossier 衍生预览生成
- 调试索引
- 非关键摘要视图

### Pointer Carrier Rule

active pointer 只允许写入现有 authoritative carriers：

- `Directive.evidence_pack_refs`
- `PlanRevision.product_spec_ref`
- `PlanRevision.execution_package_ref`
- `PlanRevision.task_graph_ref`
- `PlanRevision.active_dossier_ref`
- `DispatchIntent.run_contract_ref`
- `DispatchIntent.session_scaffold_ref`

不得新增“artifact pointer table”来反向支配 runtime truth。

### Compile Failure and Recovery Rule

若 payload 写入成功但 activate 失败：

- artifact metadata row 保持 `compiled_pending_activation`
- 不得人工把其视为 active
- recovery job 可重试 activate change-set

若 payload 写入失败：

- metadata row 标记 `failed`
- `CompilationBatch.status` 至少为 `partial` 或 `failed`
- 写 `retry_marker` 或 `reconciliation_marker`

### Canonical vs Non-Canonical Rule

允许保留调试产物，但必须满足：

- `status=failed`、`partial`、`non_canonical` 或等价状态
- 无 active pointer 指向它
- downstream 编译不得把它当 canonical source

## Protocol Steps

1. planning / replan / recovery 触发 compile。
2. 先执行 `prepare_compilation_batch` change-set，记录 batch 与输入引用。
3. 编译器把 payload 写入 `artifacts/compiled/<artifact_type>/<artifact_id>/`。
4. 计算 `payload_digest`，生成 `payload_root_uri`、`payload_entry_uri`。
5. 执行 `record_compiled_artifact` change-set，写 metadata row。
6. 全部 critical payload durable 后，执行 `activate_compiled_artifacts` change-set：
   - 更新 pointer carriers
   - supersede 旧 artifact
   - 更新 batch 状态
   - 写 outbox
7. outbox 异步发布 event log。
8. 若 activate 失败，recovery 只能重试 activate，不得假设 compile 已生效。

## State / Schema

```yaml
artifact_metadata_row:
  artifact_id: rc_20260412_07
  artifact_type: run_contract
  status: compiled_pending_activation
  compilation_batch_id: compile_20260412_04
  compiled_at: 2026-04-12T10:30:00Z
  compiled_from_refs:
    - plan_rev_18
    - task_auth_api_03
    - dispatch_auth_api_03
  payload_root_uri: artifact://run_contract/rc_20260412_07
  payload_entry_uri: artifact://run_contract/rc_20260412_07#artifact.yaml
  payload_format: yaml
  payload_digest: sha256:abc123
  dispatch_intent_id: dispatch_auth_api_03
  canonical_pointer_scope: dispatch_intent
  superseded_by_ref: null
  is_embedded_payload: false

compilation_activate_changeset:
  changeset_id: cs_20260412_091
  command_name: activate_compiled_artifacts
  object_deltas:
    - object_type: DispatchIntent
      object_id: dispatch_auth_api_03
      before:
        run_contract_ref: rc_20260412_06
      after:
        run_contract_ref: rc_20260412_07
  outbox_events:
    - event_type: CompiledArtifactActivated
      payload:
        artifact_id: rc_20260412_07
        previous_ref: rc_20260412_06
```

## Acceptance Criteria

- 读者能直接据此定义 artifact metadata 表、payload root 和 URI 规范。
- compilation batch、metadata row、pointer switch、outbox 的事务边界是明确且可编码的。
- 不会出现 payload 不存在却已切换 active pointer 的状态。
- 文档明确保证 compiled artifact 仍是 derived state，而不是新的事实源。
