# 06 vNext 实现收口 Gap Analysis

## Purpose

- 基于当前仓库文档，判断 vNext 哪些部分已经足够进入实现，哪些部分仍停留在协议层。
- 把“主协议已收敛”进一步收口为“可直接开工的实现前设计包”。
- 为首批实现提供明确的补齐入口、落地边界与剩余验证项。

## Scope

- 本文只覆盖当前仓库已定义的 vNext harness 设计范围。
- 本文不改变现有 truth hierarchy，不把 dossier、scaffold、artifact 升级为 authoritative state。
- 本文不扩展 multi-writer、multi-repo、rich UI、复杂 policy engine、完整人工审批流。
- 具体落地规范分别引用：
  - `../06-coordination/05-Compiled-Artifact-and-Compilation-Transaction-Boundaries.md`
  - `../05-execution/17-Codex-First-Adapter-Fallback-Profile.md`
  - `../04-planning/13-vNext-Minimum-Implementation-Slices-and-Phase-Plan.md`
  - `../08-appendix/15-vNext-Compiled-Artifact-Schema-Catalog.md`

## Definitions

- `足够实现`：已有对象、约束、输入输出、事务边界和验收口径，工程上可直接建表、写编译器和测试。
- `协议层`：已有目标语义和交互约束，但缺少 metadata layout、事务边界、host-side fallback 或最小测试门。
- `实现前设计包`：工程团队不再继续扩概念，而是可以直接据此拆表、写命令、建 adapter、补 fixture 和 conformance tests 的文档集合。

## Rules

### 结论总览

当前 vNext 文档状态可分为三层：

| 分层 | 当前状态 | 说明 |
|---|---|---|
| 架构主线 | 已收敛，可实现 | 输入到 spec、task graph、run contract、handoff、reset、preemption 主线已完整 |
| 编译产物落盘与事务边界 | 之前偏协议层，本轮收口为可实现 | 需补 metadata row、payload root、artifact ref URI、目录布局、compilation batch change-set 边界 |
| adapter 能力降级与第一阶段实施包 | 之前偏协议层，本轮收口为可实现 | 需补 Codex first fallback 和最小切片、命令、测试门、验收标准 |

### 已经足够实现的部分

以下主题已经具备明确的实现方向，不需要继续扩概念：

1. `truth hierarchy`
   - authoritative object state、event log、checkpoint 的层级已经稳定。
   - `launch_run` 不得伪造最终成功状态的约束已稳定。
2. `vNext planning pipeline`
   - `Directive -> Research -> Evidence -> Product Spec -> Execution Package -> Task Graph -> Run Contract` 主线已清楚。
   - freshness、selective recompile、active pointer 的基本语义已清楚。
3. `run-time control discipline`
   - handoff、independent acceptance、context reset、user interrupt、supersession、termination / reassignment 已有统一协议。
4. `first adapter choice`
   - 首适配器选 `Codex` 已收敛。
   - `restore_run` 非硬依赖已收敛。

### 之前仍停留在协议层、现已要求补齐的部分

以下主题在原文档里只有原则，缺少实现级约束：

1. `compiled artifact durable shape`
   - 缺少统一 metadata row 字段收口。
   - 缺少 payload root、artifact ref URI、目录布局规范。
   - 缺少小 payload 内嵌与大 payload 文件化的判定。
2. `compilation batch transaction boundary`
   - 缺少 compilation batch、artifact metadata row、pointer switch、outbox 之间的 change-set 规则。
   - 缺少 payload write 和 metadata commit 的先后顺序。
   - 缺少 compile failure / partial compile 的补偿 marker 约束。
3. `Codex host-side fallback`
   - 缺少 callback vs poll 的最小依赖模式。
   - 缺少 heartbeat、restore、soft_cancel、hard_kill 的保守降级路径。
   - 缺少 liveness ambiguity 时 host-side hold / reassign 规则细节。
4. `minimum implementation slice`
   - 缺少首批必须落地的对象、命令、测试门、验收标准的明确切片。
   - 缺少阶段化交付定义，导致团队容易继续抽象讨论。

### 现在仍然故意不进入实现包的部分

以下仍明确留在后续，不得借本轮收口偷偷引入：

1. multi-writer control plane
2. multi-repo federation
3. rich UI / dashboard
4. complex policy engine
5. 完整人工审批流
6. 把 dossier、scaffold、artifact 反向升级为 runtime truth

### 本轮实现前设计包的构成

本轮之后，工程实现应以以下文档组合作为直接输入：

1. `03-state-model/08-vNext-Compiled-Artifact-Package.md`
2. `04-planning/12-Compilation-Lifecycle-and-Freshness-Protocol.md`
3. `06-coordination/05-Compiled-Artifact-and-Compilation-Transaction-Boundaries.md`
4. `05-execution/17-Codex-First-Adapter-Fallback-Profile.md`
5. `04-planning/13-vNext-Minimum-Implementation-Slices-and-Phase-Plan.md`
6. `08-appendix/15-vNext-Compiled-Artifact-Schema-Catalog.md`

## Protocol Steps

1. 先用本文判断某个主题属于：
   - 已可实现
   - 需按本轮新增规范实现
   - 明确不进入当前阶段
2. 对 compiled artifact 相关实现，先读：
   - `03-state-model/08`
   - `04-planning/12`
   - `06-coordination/05`
   - `08-appendix/15`
3. 对 Codex adapter 与 recovery 相关实现，先读：
   - `05-execution/05`
   - `05-execution/13`
   - `05-execution/17`
   - `07-reliability/16`
4. 对第一阶段排期与验收，先读：
   - `04-planning/13`
5. 若新设计提议触碰 truth hierarchy 或引入排除项，必须先拒绝并回到本文边界。

## Acceptance Criteria

- 读者能明确区分哪些主题已经足够实现、哪些只是协议层、哪些明确不做。
- 读者能把 vNext 的实现入口收敛到少数几篇实现级文档，而不是继续在全仓库中来回推断。
- 本文不会改变既有 truth hierarchy，也不会引入被排除的扩展方向。
