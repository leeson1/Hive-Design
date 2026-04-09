"""AIAdvisor: uses Claude for exception handling and ambiguous scheduling decisions."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from hive.models.context import DroneContext
from hive.models.task import Task


class AdvisorAction(str, Enum):
    RETRY = "retry"
    SKIP = "skip"
    SPLIT = "split"
    ESCALATE = "escalate"


@dataclass
class AdvisorDecision:
    action: AdvisorAction
    reasoning: str
    modified_description: Optional[str] = None  # For RETRY with adjusted approach
    new_tasks: Optional[list[dict]] = None       # For SPLIT

    @classmethod
    def escalate(cls, reasoning: str) -> "AdvisorDecision":
        return cls(action=AdvisorAction.ESCALATE, reasoning=reasoning)


ADVISOR_SYSTEM_PROMPT = """You are the Drone AI advisor for the Hive orchestration system.
Your job is to make scheduling decisions when tasks are blocked or fail.

Respond with a JSON object:
{
  "action": "retry" | "skip" | "split" | "escalate",
  "reasoning": "<brief explanation>",
  "modified_description": "<new task description if action=retry>",
  "new_tasks": [<task objects if action=split>]
}

Guidelines:
- RETRY: If the task failed due to a fixable issue (transient error, wrong approach). Provide a modified description.
- SKIP: If the task is not actually needed given current project state.
- SPLIT: If the task is too large/complex. Provide 2-4 smaller subtasks.
- ESCALATE: If human judgment is genuinely required. Use sparingly.
"""


class AIAdvisor:
    def __init__(self, project_root: Path, max_budget_usd: float = 0.50):
        self.project_root = project_root
        self.max_budget_usd = max_budget_usd

    async def decide_on_blocked_task(
        self, ctx: DroneContext, task: Task
    ) -> AdvisorDecision:
        prompt = self._build_prompt(ctx, task)
        try:
            result_text = await self._claude_call(prompt)
            data = json.loads(result_text)
            return AdvisorDecision(
                action=AdvisorAction(data["action"]),
                reasoning=data.get("reasoning", ""),
                modified_description=data.get("modified_description"),
                new_tasks=data.get("new_tasks"),
            )
        except Exception as e:
            return AdvisorDecision.escalate(f"AI advisor error: {e}")

    def _build_prompt(self, ctx: DroneContext, task: Task) -> str:
        recent = "\n\n".join(ctx.recent_handovers[-3:]) if ctx.recent_handovers else "None"
        return f"""A task is blocked and needs a scheduling decision.

## Blocked Task
ID: {task.id}
Title: {task.title}
Description: {task.description}
Blocked Reason: {task.blocked_reason or 'Unknown'}
Retry Count: {task.retry_count}/{task.max_retries}

## Global Project State
{ctx.global_state[:2000]}

## Recent Handovers (context)
{recent[:2000]}

## Plan Index
{ctx.plan_index[:1000]}

Decide what to do with this blocked task."""

    async def _claude_call(self, prompt: str) -> str:
        cmd = [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--system-prompt", ADVISOR_SYSTEM_PROMPT,
            "--max-budget-usd", str(self.max_budget_usd),
            "--permission-mode", "default",
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.project_root),
        )
        stdout, _ = await proc.communicate()
        data = json.loads(stdout)
        if data.get("is_error"):
            raise RuntimeError(data.get("result", "unknown error"))
        return data["result"]
