# 16 Run Termination and Reassignment Matrix

## Purpose

- 定义 Hive 对 active run 的终止、回收、重派与 supersede 决策矩阵。
- 把 `finish_current_step / soft_stop / hard_kill / rehydrate + reassign / supersede` 从分散规则收敛为统一协议。
- 明确在 adapter 能力不确定时，控制平面应如何保守降级。

## Scope

- 本文覆盖 active `AgentRun` 的 termination mode、partial handoff 回收、reassign gate 与 fallback 行为。
- 本文不改变 `Task`、`AgentRun`、`Lock`、`Checkpoint` 的事实层级。
- 用户插话协议见 `15-User-Interrupt-Replan-and-Preemption-Protocol.md`。
- context reset handoff 见 `14-Context-Reset-and-Session-Handoff-Protocol.md`。
- 执行器能力不确定性的前提见 `../05-execution/13-First-Executor-Profile.md`。

## Definitions

- `Termination Mode`：控制平面希望对当前 run 施加的停止方式。
- `finish_current_step`：允许 worker 收尾当前最小工作单元后退出。
- `soft_stop`：请求 worker 尽快有序停止，并尽量提交 partial handoff。
- `hard_kill`：立即终止运行实例，不等待其有序退出。
- `rehydrate + reassign`：不依赖恢复原 run，而是从外部状态重建最小上下文后派发新 run。
- `Supersede`：当前 task / run 的产出仍保留，但主推进路径被新 revision / 新 task 替代。
- `Launch Ambiguity`：`launch_run` 已发出，但控制平面无法判定 run 是否真正存活。
- `Unknown Live Run`：由于进程重启、网络中断或 adapter 观测不足，控制平面无法确认 run 是否仍活着。

## Rules

### 总规则

1. termination decision 必须基于 authoritative object state、adapter 观测和 recovery evidence，而不是聊天推断。
2. 终止 run 不等于任务完成；完成仍需 `Handoff + Acceptance`。
3. 当 adapter 能力不确定时，控制平面必须选择保守路径，不得假设 stop / kill / restore 已成功。
4. 只要存在有价值进展，优先尝试保留 `Partial Handoff`。

### Capability-Uncertain Fallback Rule

当以下能力未被验证为 hard dependency 时：

- `restore_run`
- `soft_cancel`
- `hard_kill` fidelity
- built-in heartbeat fidelity

必须采用保守降级：

- 不把“已发送 stop/kill 请求”当作 run 已停止的事实。
- 在 live / dead 未判明前，冲突路径上的锁优先转为 `recovery_hold`。
- 优先通过 `poll_run(...)`、log collection、artifact collection 与 workspace 观察补证。
- 无法安全恢复原 run 时，默认走 `rehydrate + reassign`。

### Partial Handoff Rule

- `finish_current_step` 与 `soft_stop` 默认要求 partial handoff 或完整 handoff。
- `hard_kill` 若来不及提交 handoff，控制平面仍必须尽量回收：
  - workspace snapshot
  - 原始日志
  - 已产出的 artifact refs
  - 未决 issue
- 拿不到 partial handoff 时，后续 reassign 必须显式标记 `evidence_gap`，并让新 run 先做更严格 bootstrap / smoke-check。

### Reassign Gate

只有满足以下条件，才允许安全重派：

- 当前 task 未被终结为 `cancelled` 或永久 `blocked`
- 原 run 的 live / dead 状态已判明，或相关冲突路径已进入安全 `recovery_hold`
- 最新可用 `Checkpoint` 已存在
- 最近 `Handoff / Partial Handoff / workspace snapshot` 已尽量回收
- replacement run 的 `TaskSpec / Run Contract` 已显式引用回收证据或 `evidence_gap`

### Supersede Rule

- `Supersede` 是 planning 决策，不只是“换个 worker”。
- 被 supersede 的旧 run 若仍有价值，应优先 `finish_current_step` 或 `soft_stop`，回收 partial handoff。
- 只有在继续运行会扩大错误面、越界写入或明显违背新方向时，才优先 `hard_kill`。

### Termination Decision Matrix

| Trigger | 首选动作 | adapter 能力不确定时的降级 | Partial Handoff 期望 | 后续动作 |
|---|---|---|---|---|
| 用户插话，要求 `pause` | `finish_current_step` | 若无法确认有序收尾，则 `soft_stop` + recovery hold | 必须尽量拿到 | checkpoint 后等待 resume / reassign |
| 用户插话，要求 `cancel` | `soft_stop` 或 `hard_kill`，取决于风险 | 若 stop/kill 结果不确定，则保留 recovery hold 直到 live/dead 判明 | 最佳努力 | 释放或转 hold，更新 ledger |
| 用户插话，要求 `supersede` | `finish_current_step` 或 `soft_stop` | 若继续运行风险高，则退化为 `hard_kill` | 默认要求 | 创建 replacement task / contract |
| heartbeat timeout | 先进入 recovery，默认 `rehydrate + reassign` | 不假设原 run 已死；先 poll / collect evidence | 最佳努力 | reassign 或 block |
| launch ambiguity | 不直接 kill；先判定 live / dead | recovery hold + 二次观测 | 通常拿不到 | 明确 live/dead 后再 reassign |
| unknown live run after restart/reset | recovery hold + liveness probe | 不做重复派发直到冲突可控 | 视情况 | `rehydrate + reassign` 或 resume |
| operator manual stop | `soft_stop` 优先，必要时 `hard_kill` | kill 不可信时保留 hold 并收证 | 最佳努力 | 由 operator / recovery 决定 reassign |
| worker 明确上报 blocked 且上下文仍有价值 | `finish_current_step` | 若已无法继续，则 `soft_stop` | 应提供 | followup planning / reassign |

### Trigger-Specific Rule

#### Timeout

- timeout 不是“立刻新建 run”。
- 必须先进入 recovery，判断：
  - heartbeat 是否真缺失
  - run 是否可能仍在写入
  - 是否已有可回收 artifacts
- 若无法安全恢复原 run，默认 `rehydrate + reassign`。

#### Launch Ambiguity

- `launch_run` 发出后未 ack，不得假设“没启动成功”。
- 必须先把相关 lock 置于 `recovery_hold` 或等价安全状态。
- 只有在 live / dead 判明，或 workspace 已隔离到不会冲突时，才允许 replacement dispatch。

#### Unknown Live Run

- 在 control plane 重启、context reset 或 adapter 瞬断后，若 run 是否存活不明，必须先做 liveness probe。
- probe 失败不等于 run 死亡；要结合日志时间戳、workspace 变化、外部 side effect token 综合判断。

#### Manual Stop

- operator / user 主动停止时，也必须走同样的 handoff / recovery 记录。
- 不能因为是人工操作就跳过 partial handoff、checkpoint 或 ledger 更新。

## Protocol Steps

1. 识别 termination trigger。
2. 评估：
   - user intent
   - live / dead certainty
   - path conflict risk
   - adapter capability certainty
3. 选择 `finish_current_step / soft_stop / hard_kill / rehydrate + reassign / supersede`。
4. 尽量收集 `Partial Handoff`、workspace snapshot、logs、artifacts。
5. 更新 `Task / AgentRun / Lock / RecoveryAction / Checkpoint`。
6. 若满足 `Reassign Gate`，生成 replacement `Run Contract` 并派发新 run。
7. 若不满足，则 block 当前 workline，并记录 `evidence_gap` 或 pending decision。

## State / Schema

```yaml
run_termination_decision:
  decision_id: term_20260411_04
  run_id: run_exec_15
  trigger: heartbeat_timeout
  live_certainty: unknown
  preferred_action: rehydrate_and_reassign
  attempted_stop_mode: soft_stop
  adapter_capability_confidence:
    soft_cancel: low
    hard_kill: unknown
    restore_run: unsupported
  partial_handoff_expected: best_effort
  evidence_gap: false
  followup_action:
    type: replacement_run_contract
    ref: rc_20260411_08
```

## Anti-patterns

- 只要超时就直接二次派发，不先处理 live / dead 歧义。
- stop / kill 请求刚发出去，就当成 run 已经停止。
- 旧 run 被 supersede 后直接丢弃中间产物。
- 没拿到 partial handoff，却不标记 `evidence_gap` 就让新 worker 继续。
- 把 `restore_run` 当成必然存在的能力。

## Acceptance Criteria

- 文档明确给出不同 trigger 下的 termination / reassignment 决策矩阵。
- adapter 能力不确定时的降级策略被显式写死。
- partial handoff 能拿到与拿不到两种情况都有后续处理。
- timeout、launch ambiguity、unknown live run、manual stop、user interrupt 都有标准处理路径。
