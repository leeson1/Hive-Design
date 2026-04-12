# 17 Codex First Adapter Fallback Profile

## Purpose

- 把 `Codex first adapter` 从能力选择收口为 host-side 可执行 fallback 规范。
- 明确 callback vs poll、heartbeat、restore、soft_cancel、hard_kill 在未验证前的保守依赖模式。
- 给首版 `codex` adapter 与 recovery worker 提供统一行为基线。

## Scope

- 本文只覆盖 `Codex` 作为 first adapter 时，Hive host-side 必须承担的 fallback 行为。
- 本文不宣称这些能力已被真实验证为 hard dependency。
- 抽象契约仍以 `05-executor-adapter-contract.md` 为准。
- 首适配器选择见 `13-First-Executor-Profile.md`。
- 终止与重派矩阵见 `../07-reliability/16-Run-Termination-and-Reassignment-Matrix.md`。

## Definitions

- `Callback Signal`：由 adapter 主动推送给控制平面的状态更新。
- `Poll Signal`：由控制平面主动调用 `poll_run(...)` 获得的状态更新。
- `Host-side Heartbeat`：由 Hive 基于 poll、日志时间戳、artifact 更新时间推导出的 liveness 观察。
- `Restore Candidate`：理论上可尝试恢复的 run，但尚未验证具备 run-fidelity restore。
- `Soft Cancel Requested`：已请求优雅停止，但尚未把 run 视为已停止。
- `Hard Kill Requested`：已请求强制终止，但尚未把 run 视为已死亡。

## Rules

### Dependency Rule

首版 `codex` adapter 只能把以下能力当 hard dependency：

- `launch_run`
- `poll_run`
- `collect_logs`
- `collect_artifacts`
- workspace isolation baseline

以下能力一律不是 hard dependency：

- callback delivery fidelity
- built-in heartbeat fidelity
- `restore_run` fidelity
- `soft_cancel` fidelity
- `hard_kill` fidelity

### Callback vs Poll Rule

首版必须采用 `poll-first, callback-optional` 模式：

- callback 只能作为加速信号
- poll 才是 canonical runtime observation

规则：

- callback 到达时，可以触发一次快速 reconcile
- callback 未到达，不得据此推断 run 不存在
- callback 与 poll 冲突时，以 poll + durable evidence 为准

### Heartbeat Rule

首版 heartbeat 必须由 host-side 推导，至少组合以下来源：

- 最近一次 `poll_run(...)` 返回时间
- adapter 可收集日志的最新时间戳
- artifact / workspace 文件更新时间

推荐状态：

- `live_confirmed`
- `possibly_live`
- `stale_observed`
- `unknown`

规则：

- 单次观测缺失不得直接判死。
- 只有连续超过 `start_sla` 或 `heartbeat_timeout`，且多信号均无进展时，才进入 recovery。
- heartbeat stale 触发 recovery，不直接触发 duplicate dispatch。

### Restore Rule

首版 `restore_run(...)` 只能作为 best-effort probe：

- 可以尝试恢复或重新附着
- 不得把“成功附着到某个会话”当成“已恢复原 run fidelity”

只有满足以下条件才可把 restore 结果用于 resume：

- 仍绑定原 workspace
- 仍绑定原 task / dispatch intent
- 可确认未产生第二个冲突 run
- 近端日志 / artifacts 与原 run lineage 一致

否则默认走：

- `rehydrate + reassign`

### Soft Cancel Rule

`cancel_run(...)` 返回成功只表示“停止请求已发出”，不表示 run 已停止。

host-side 必须继续：

- poll run 状态
- 收集最后日志
- 尝试收集 partial handoff / artifacts
- 在必要时将锁保持为 `recovery_hold`

只有满足以下条件，才可把 run 视为已停止：

- poll 明确显示 exited / cancelled / failed
- 或长时间无活动且 workspace 已确认无继续写入风险

### Hard Kill Rule

`kill_run(...)` 返回成功只表示“强制终止请求已发出”，不表示 process 必然已经死亡。

host-side 必须：

- 继续执行 liveness probe
- 回收 workspace snapshot、logs、已产出 artifacts
- 若 live/dead 仍不确定，则保持冲突路径锁为 `recovery_hold`

只有在高风险场景才优先 hard kill：

- 明显越界写入
- 已违反 superseded direction
- 持续扩散错误面

### Launch Ambiguity Rule

若 `launch_run(...)` 后无确定 ack：

- `AgentRun` 保持 `created` 或等价未确认状态
- `Task` 保持 `dispatching`
- 锁保持 `reserved` 或 `recovery_hold`
- 不得直接二次派发

host-side 后续动作：

- poll 是否存在 live run
- 收集工作区变化
- 超过 start SLA 后进入 recovery

### Host-side Fallback Matrix

| 能力 | 首选路径 | 未验证时的 hard 依赖结论 | host-side fallback |
|---|---|---|---|
| callback | callback + reconcile | 不是 hard dependency | 周期 poll，callback 仅作提示 |
| heartbeat | adapter 提供 | 不是 hard dependency | poll + log ts + artifact ts 合成 heartbeat |
| restore | restore_run | 不是 hard dependency | `rehydrate + reassign` |
| soft_cancel | cancel_run | 不是 hard dependency | 请求停止后继续 poll，并保留 recovery hold |
| hard_kill | kill_run | 不是 hard dependency | kill 后继续 liveness probe，并回收快照 |

### Evidence Collection Rule

无论 callback、cancel、kill、restore 哪条路径，host-side 都必须尽量回收：

- normalized status history
- raw logs
- artifact refs
- workspace snapshot 或文件修改摘要
- last known heartbeat observation
- evidence gap 标记

### Acceptance Boundary Rule

adapter fallback 不改变 acceptance 边界：

- run 结束不等于 task 完成
- partial handoff 不等于 accepted
- restore 成功不等于恢复了任务正确性

## Protocol Steps

1. `launch_run(...)` 后立即进入 `poll-first` 监控。
2. 若收到 callback，仅触发加速 reconcile，不改变 canonical observation 规则。
3. 周期执行：
   - `poll_run(...)`
   - `collect_logs(...)`
   - `collect_artifacts(...)`
4. host-side 生成 heartbeat observation。
5. 若需要停止：
   - 先 `cancel_run(...)`，若风险高再 `kill_run(...)`
   - 停止请求后继续 poll 与证据回收
6. 若 run 丢失、超时或宿主重启：
   - 尝试 `restore_run(...)` 作为 probe
   - 未满足 fidelity gate 时改走 `rehydrate + reassign`
7. 更新 `AgentRun`、`Task`、`Lock`、`RecoveryAction`，再由 acceptance / recovery 决定下一步。

## State / Schema

```yaml
codex_host_observation:
  run_id: run_codex_20260412_03
  callback_seen: false
  last_poll_at: 2026-04-12T11:20:00Z
  last_log_ts: 2026-04-12T11:19:41Z
  last_artifact_ts: 2026-04-12T11:19:10Z
  heartbeat_state: possibly_live
  restore_confidence: low
  soft_cancel_requested: true
  hard_kill_requested: false
  canonical_action_if_timeout: rehydrate_and_reassign
```

## Acceptance Criteria

- `Codex` adapter 首版可在不依赖 callback、restore、soft cancel、hard kill fidelity 的情况下工作。
- callback vs poll 的主从关系明确，不会把 callback 缺失误判为 run 消失。
- stop / kill 请求后不会被错误当成 run 已停止。
- 文档明确规定 host-side fallback 与 evidence collection，而不是把关键判断外包给 adapter。
