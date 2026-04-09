"""WorkerRunner: manages Claude Code subprocess lifecycle for a single task."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from hive.drone.state_machine import TaskStateMachine
from hive.hive_dir import HiveDir
from hive.models.handover import HandoverMemo
from hive.models.task import Task, TaskStatus
from hive.worker.prompt_builder import PromptBuilder
from hive.worker.verifier import WorkerVerifier


WORKER_TIMEOUT_SECONDS = 3600   # 1 hour hard limit per task
DEFAULT_BUDGET_PER_TASK = 5.0   # USD


@dataclass
class WorkerResult:
    success: bool
    task: Task
    memo: Optional[HandoverMemo] = None
    error: Optional[str] = None
    cost_usd: float = 0.0
    duration_seconds: float = 0.0


class WorkerRunner:
    def __init__(
        self,
        hive_dir: HiveDir,
        project_root: Path,
        state_machine: TaskStateMachine,
        budget_per_task: float = DEFAULT_BUDGET_PER_TASK,
    ):
        self.hd = hive_dir
        self.project_root = project_root
        self.sm = state_machine
        self.prompt_builder = PromptBuilder(hive_dir)
        self.verifier = WorkerVerifier(hive_dir)
        self.budget_per_task = budget_per_task

    async def run_task(
        self, task: Task, all_tasks: dict[str, Task]
    ) -> WorkerResult:
        # 1. Transition to ACTIVE
        task = self.sm.transition(self.hd, task, TaskStatus.ACTIVE)

        # 2. Build worker context and prompts
        ctx = self.prompt_builder.build_context(task, all_tasks)
        user_prompt = self.prompt_builder.build_user_prompt(ctx)
        system_prompt = self.prompt_builder.build_system_prompt(ctx)

        # 3. Launch claude subprocess
        cmd = [
            "claude",
            "-p", user_prompt,
            "--output-format", "json",
            "--system-prompt", system_prompt,
            "--permission-mode", "acceptEdits",
            "--max-budget-usd", str(self.budget_per_task),
            "--add-dir", str(self.project_root),
        ]

        start = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root),
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=WORKER_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            proc.kill()
            return await self._handle_failure(task, "timeout after 1 hour")
        except Exception as e:
            return await self._handle_failure(task, f"subprocess error: {e}")

        duration = time.monotonic() - start

        # 4. Parse subprocess JSON output
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError as e:
            return await self._handle_failure(
                task, f"malformed JSON output: {e}\nstderr: {stderr.decode()[:500]}"
            )

        if result.get("is_error"):
            return await self._handle_failure(
                task, result.get("result", "unknown claude error")
            )

        cost = result.get("total_cost_usd", 0.0)

        # 5. Load handover memo written by worker
        memo = self.verifier.load_handover(task)
        if memo is None:
            # Worker completed but didn't write handover - synthesize minimal one
            memo = self.verifier.synthesize_memo(task, result, duration)
            self.hd.save_handover(memo)

        # 6. Validate exit criteria
        verification = self.verifier.check_exit_criteria(task, memo)
        if not verification.all_met and task.retry_count < task.max_retries:
            unmet_str = "; ".join(verification.unmet)
            return await self._handle_retry(
                task, f"exit criteria not met: {unmet_str}"
            )

        # 7. Transition to DONE
        task = self.sm.transition(self.hd, task, TaskStatus.DONE)
        self.hd.save_handover(memo)

        return WorkerResult(
            success=True,
            task=task,
            memo=memo,
            cost_usd=cost,
            duration_seconds=duration,
        )

    async def _handle_failure(self, task: Task, reason: str) -> WorkerResult:
        if task.retry_count < task.max_retries:
            return await self._handle_retry(task, reason)
        task = self.sm.transition(
            self.hd, task, TaskStatus.BLOCKED,
            reason=f"exhausted {task.max_retries} retries: {reason}",
        )
        self.hd.write_pending(task.id, f"Task blocked after {task.retry_count} retries.\n\nReason: {reason}")
        return WorkerResult(success=False, task=task, error=reason)

    async def _handle_retry(self, task: Task, reason: str) -> WorkerResult:
        task.retry_count += 1
        task.blocked_reason = reason
        task = self.sm.transition(
            self.hd, task, TaskStatus.QUEUE,
            reason=f"retry {task.retry_count}: {reason}",
        )
        self.hd.save_task(task)
        return WorkerResult(success=False, task=task, error=f"retry {task.retry_count}: {reason}")
