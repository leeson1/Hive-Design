# 10 Benchmark Repo Research Protocol

## Purpose

- 定义 Hive 在规划阶段如何使用“同类仓库 / 参考实现”作为受控研究输入。
- 保证 benchmark repo 研究有边界、有去重、有质量门，而不是变成全网漫游。
- 说明 repo 观察结果如何进入 `Evidence Pack`，再被编译为后续 planning 输入。

## Scope

- 本文覆盖 benchmark repo research 的触发条件、来源优先级、选择规则、去重规则、停止条件与编译规则。
- 本文不改变 `Research Sprint -> Evidence Pack -> Plan Compilation` 的主链，只补充 repo examples 这一类输入的专门协议。
- `Research Sprint` 的通用定义见 `03-research-sprint-spec.md`。
- `Evidence Pack` 的输出约束见 `04-evidence-pack-spec.md`。

## Definitions

- `Benchmark Repo`：被选入本轮调研、用于观察实现模式、边界与验证路径的参考仓库。
- `Repo Observation`：对 benchmark repo 某一实现点的结构化观察记录，必须可回到具体证据位置。
- `Repo Family`：共享同一模板、同一上游、同一派生链或高度重复结构的一组仓库。
- `Normative Source`：对语义和约束具有更高优先级的来源，例如官方文档、标准和规范。
- `Illustrative Source`：只用于观察实现模式的来源，例如 example repo、博客文章或社区教程。

## Rules

### 何时必须拉起 benchmark repo research

满足任一条件时，`Research Sprint` 必须显式评估是否需要 benchmark repo research：

- 需求涉及新的技术栈、框架组合或基础设施模式。
- 存在多个可行实现路径，需要比较“别人实际上怎么做”。
- 用户明确要求“看同类型项目”或“参考现有仓库实现”。
- 官方文档只给出能力说明，没有给出足够的工程落地模式。
- 当前仓库与既有 `Charter` 无法给出足够稳定的本地先例。

### 何时可以跳过 benchmark repo research

满足全部条件时，可以跳过：

- 当前仓库或同类内部模板已经提供足够先例。
- 需求主要是局部增量，不涉及新的实现模式选择。
- 官方文档与既有项目边界已经足够回答核心问题。
- 本轮 planning 的关键未知不在实现模式，而在需求澄清或验收标准。

### 来源优先级

不同来源的优先级必须显式区分：

| 优先级 | 来源类型 | 用途 | 可否直接成为约束 |
|---|---|---|---|
| P1 | 官方文档 / 标准 / 规范 | 语义、协议、限制、推荐用法 | 只能在编译后进入约束 |
| P2 | 当前仓库 / 既有内部实现 / 已接受模板 | 本地适配、组织约束、已有工作方式 | 只能在编译后进入约束 |
| P3 | benchmark repos / example repos | 观察实现模式、比较候选方案、提取风险 | 不能直接进入约束 |
| P4 | 博客 / 文章 / 教程 | 辅助寻找线索或补充背景 | 不能直接进入约束 |

规则：

- 当 P1 与 P3/P4 冲突时，默认以 P1 为准。
- 当 P2 与外部 benchmark repo 冲突时，必须在 `Evidence Pack` 中显式记录差异、上下文与是否采纳。
- 博客 / 文章只能作为线索来源，不得单独支撑高置信 claim。

### Selection Rule

每个 benchmark repo entry 至少必须记录：

- `repo_id`
- `repo_ref`
- `selection_reason`
- `repo_family_key`
- `source_type`
- `license_assessment`
- `freshness_assessment`
- `quality_assessment`
- `focus_topics`
- `observation_budget`

选择规则：

- 默认 `max_repo_examples = 3`，与 `Research Sprint` 预算保持一致。
- 只有在存在多个明显不同实现流派时，才允许扩展到 5 个，并必须记录扩展理由。
- 优先选“实现路径不同”的仓库，而不是选“同一模板换皮”的仓库。
- 优先选与本轮问题直接相关的子系统，而不是全项目大而全对比。
- 若候选仓库来自同一 `Repo Family`，默认只保留一个代表样本。

### De-duplication Rule

以下情况默认视为重复或近重复来源，应合并或降权：

- fork 后仅做少量品牌或配置改动
- 同一上游模板生成的多个示例仓库
- 同一组织内结构、依赖与脚手架高度一致的多个仓库
- 一篇博客直接配套的 demo repo 与文中代码片段

去重后必须保留：

- 保留的 canonical repo ref
- 被合并或降权的 refs
- 去重原因

### License / Freshness / Quality Rule

对每个 benchmark repo 必须做三类评估：

1. `license_assessment`
   - 许可证未知时，不得把该 repo 作为可复用实现样本。
   - 许可证明确不适合复制代码时，只能抽取模式观察，不得形成“可直接借鉴实现”结论。
2. `freshness_assessment`
   - 明显依赖过时框架版本、废弃 API 或不再维护的仓库，必须降为低置信参考。
   - 若过时实现仍揭示稳定架构模式，可保留为历史选项，但必须标记风险。
3. `quality_assessment`
   - 缺少测试、结构混乱、错误较多、与目标问题无关的仓库，必须降权或剔除。
   - 低质量样例只能用于列出风险，不得主导推荐方案。

### Observation Discipline

- repo 观察必须是 bounded read，不得演化为“把整个参考仓库读一遍”。
- 每条观察必须绑定到具体文件、模块、提交、README 段落或配置项。
- benchmark repo 只能提供 `claims / options / risks / validation_candidates` 的上游输入。
- benchmark repo 不能直接生成 `Task`、`Run Contract` 或运行态约束。

### Evidence Pack Compilation Rule

repo 观察进入 `Evidence Pack` 时，至少应产生以下一种结构化结果：

- `claim`
  - 例：某类系统普遍把长时任务状态外置到 DB，而不是依赖 executor 会话。
- `option`
  - 例：使用 `worktree-per-run` 与 `shared-repo + strict path lock` 两种工作区模式。
- `risk`
  - 例：某类参考实现强依赖内建会话恢复，不适合作为 Hive MVP 先验。
- `validation_candidate`
  - 例：基于参考实现共性补充 smoke-check 或 integration validation。

规则：

- 任何来自 repo observation 的结论都必须带 `evidence_refs`。
- 任何“推荐采用”的结论都必须显式说明：为什么与 Hive 当前边界兼容。
- 任何“暂不采用”的候选模式都必须说明拒绝理由，而不是静默丢弃。

### Stop Rule

满足任一条件时，benchmark repo research 应停止：

- 核心研究问题已经得到足够回答。
- 已达到 `max_repo_examples` 或 observation budget。
- 新样本只是在重复已有模式，没有新增信息。
- 已发现必须升级到用户或决策层的冲突。

## Protocol Steps

1. `Planning Coordinator` 或 `Research Agent` 判断本轮是否需要 benchmark repo research。
2. 在 `Research Sprint` 中写明：
   - 研究问题
   - 关注主题
   - 来源优先级
   - repo example budget
3. 收集候选 benchmark repos，并做 `Repo Family` 去重。
4. 对保留样本执行 license / freshness / quality 评估。
5. 在 bounded scope 内读取关键文件、README、配置、测试或相关提交。
6. 将观察归一化为 `Repo Observation`。
7. 编译到 `Evidence Pack` 的 `claims / options / risks / validation_candidates`。
8. 若存在冲突或空白，记录为 `open_questions` 或 `Issue`。

## State / Schema

```yaml
benchmark_repo_entry:
  repo_id: bench_auth_repo_01
  repo_ref: github:example-org/auth-service-template
  selection_reason: 对比 session 刷新与权限边界拆分方式
  repo_family_key: auth_service_template_v3
  source_type: benchmark_repo
  license_assessment: observe_only
  freshness_assessment: current
  quality_assessment: acceptable
  focus_topics:
    - auth_session
    - permission_boundary
  observation_budget:
    max_files: 8
    max_commits: 3
repo_observation:
  observation_id: ro_auth_01
  repo_id: bench_auth_repo_01
  evidence_refs:
    - file: src/auth/session.ts
    - file: tests/auth.integration.test.ts
  extracted_claims:
    - auth_refresh_path_separated_from_permission_check
  extracted_risks:
    - assumes_builtin_session_restore
  validation_candidates:
    - auth_integration_smoke
```

## Anti-patterns

- 把 benchmark repo research 做成全网漫游，不写问题边界和 budget。
- 选 5 个看起来差不多的 template repo，当作“充分比较”。
- 不做 license / freshness / quality 评估，直接抄实现风格。
- 只保留总结，不保留具体 evidence refs。
- 把参考仓库里的实现细节直接写成 Hive 运行态约束。

## Acceptance Criteria

- 任一 benchmark repo 都能说明为什么被选中、为什么没被去重。
- 任一 repo 观察都能回到具体 evidence refs。
- 任一通过 benchmark repo 得出的建议都能进入 `Evidence Pack`，而不是散落在自由文本里。
- 文档明确限制了 repo example 数量、去重规则、许可证和过时实现的处理方式。
