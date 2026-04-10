# 14 MVP Repo Layout

## Purpose

- 给出首个 Hive 控制平面原型仓的推荐目录布局。
- 让工程师能直接开始搭建 repo skeleton，而不是再猜模块怎么落。
- 作为 `03-MVP-Implementation-Blueprint.md` 的详细目录补充。

## Scope

- 本文描述首版实现仓的推荐语义布局。
- 目录名是语义建议，可映射到具体语言的 package / module / namespace。
- 本文不绑定具体编程语言。

## Recommended Layout

```text
hive-control-plane/
├── README.md
├── docs/
├── config/
│   ├── default.yaml
│   └── profiles/
├── migrations/
│   └── sqlite/
├── schemas/
│   └── canonical/
├── apps/
│   └── control-plane/
├── packages/
│   ├── ids-and-enums/
│   ├── schema-validation/
│   ├── persistence/
│   ├── changesets/
│   ├── intake/
│   ├── directives/
│   ├── planning/
│   ├── scheduler/
│   ├── locks/
│   ├── runs/
│   ├── acceptance/
│   ├── recovery/
│   ├── checkpointing/
│   ├── eventing/
│   ├── adapters/
│   │   ├── base/
│   │   └── codex/
│   └── conformance/
├── tests/
│   ├── fixtures/
│   ├── integration/
│   ├── conformance/
│   └── e2e/
└── var/
    ├── state/
    ├── artifacts/
    ├── logs/
    ├── workspaces/
    └── exports/
```

## Top-level Directories

| 目录 | 作用 | 首版要求 |
|---|---|---|
| `docs/` | 实现仓自身设计说明、运维说明、接口说明 | 至少保留 setup、runtime、storage、testing 三类文档 |
| `config/` | 运行配置与 profile | 至少支持本地单机 profile |
| `migrations/` | SQLite schema migrations | 必须可独立运行与回滚失败检测 |
| `schemas/` | canonical schema 生成物或镜像 | 可选，但建议保留 validator 输入 |
| `apps/control-plane/` | 主入口：sync ingress + runtime loop | 必须存在 |
| `packages/` | 所有 first-class 模块实现 | 必须存在 |
| `tests/` | fixture、integration、conformance、e2e | 必须存在 |
| `var/` | 本地 state DB、artifacts、logs、workspaces | 必须存在 |

## `apps/control-plane/`

首版建议只保留一个主应用入口，负责：

- 启动 sync ingress
- 启动 runtime loop
- 初始化 SQLite 与 filesystem roots
- 注册 `codex` adapter
- 加载 migrations
- 启动 health / admin surface（如果需要）

首版不建议先拆出：

- 独立 API app
- 独立 worker app
- 独立 publisher app

## `packages/` Modules

### Core Foundation

| 模块 | 作用 |
|---|---|
| `ids-and-enums/` | canonical IDs、status enums、event names、command names |
| `schema-validation/` | schema validator、payload parser、canonicalization helpers |
| `persistence/` | repositories、migration runner、transaction helpers |
| `changesets/` | `ChangeSet Builder`、`ChangeSet Applier`、outbox integration |

### Control-plane Domain

| 模块 | 作用 |
|---|---|
| `intake/` | `submit_user_input` handler、raw intake ingest |
| `directives/` | `compile_directive`、impact analysis |
| `planning/` | `compile_plan`、task draft generation、revision chain |
| `scheduler/` | ready set selection、capacity、dispatch ordering |
| `locks/` | path lock calculation、stale lock recovery helpers |
| `runs/` | `prepare_dispatch`、`launch_run`、run lifecycle handlers |
| `acceptance/` | acceptance input set、decision logic、followup generation |
| `recovery/` | recovery action planning、requeue / reassign logic |
| `checkpointing/` | checkpoint summary generation、checkpoint supersession |
| `eventing/` | outbox publisher、event log append、cursor helpers |
| `adapters/base/` | executor adapter contract、shared capability profile logic |
| `adapters/codex/` | 首版 `codex` adapter 实现 |
| `conformance/` | fake adapter、fixture loaders、gate runners |

## `tests/` Layout

### `tests/fixtures/`

至少建议包含：

- `schema/`
- `canonical/`
- `changesets/`
- `events/`
- `scenarios/`
- `adapters/fake_codex/`

### `tests/integration/`

建议覆盖：

- SQLite transaction / migration
- filesystem artifact refs
- outbox -> event log publish
- serialized writer behavior

### `tests/conformance/`

建议覆盖：

- schema gate
- idempotency gate
- duplicate dispatch gate
- stale lock gate
- replay safety gate

### `tests/e2e/`

建议直接承接：

- 场景 A：新项目启动
- 场景 B：运行中 directive / supersession
- 场景 C：timeout recovery

## `var/` Runtime-owned Directories

| 目录 | 用途 | 是否 authoritative |
|---|---|---|
| `var/state/` | SQLite 数据库、可能的 DB backups | 是，针对结构化对象 |
| `var/artifacts/` | patches、reports、screenshots、test outputs | 否，引用对象在 DB 中 |
| `var/logs/` | normalized terminal logs、adapter logs | 否 |
| `var/workspaces/` | run workspace / worktree / archive | 否 |
| `var/exports/` | checkpoint export、debug dumps | 否 |

## Recommended Module Ownership

首版建议的 ownership 划分：

- `apps/control-plane/` 只负责 bootstrap，不写业务判断。
- `packages/*` 负责领域逻辑。
- `persistence/` 与 `changesets/` 负责 durable boundary。
- `adapters/` 只负责 executor 差异，不负责 task completion。
- `conformance/` 不进入生产运行路径。

## Split-later Guidance

首版目录现在就应允许后续拆分，但不应先实现为多部署单元。

后续若要拆：

- `apps/control-plane/` 可拆成 `api` 与 `runtime`
- `eventing/` 可抽成独立 publisher
- `acceptance/` 与 `recovery/` 可抽成独立 worker

但在 MVP 阶段：

- 目录先分，进程先不分

## Anti-patterns

- 目录以“今天谁来写”命名，而不是以稳定模块职责命名。
- 直接在 `apps/control-plane/` 塞满所有 handler、SQL、adapter、测试工具。
- 没有 `tests/fixtures/`，导致 conformance 只能靠 ad hoc 手工验证。
- `var/` 里既放 authoritative state，又放无法区分的临时文件。

## Acceptance Criteria

- 工程师能据此创建首个实现仓的目录 skeleton。
- 读者能明确知道每个顶层目录与模块目录的职责。
- 目录布局与单 writer、SQLite + filesystem、Codex first adapter 的选择保持一致。
