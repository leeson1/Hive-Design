"""PromptBuilder: constructs the briefing injected into each Worker Claude instance."""

from __future__ import annotations

from hive.hive_dir import HiveDir
from hive.models.context import WorkerContext
from hive.models.task import Task


WORKER_SYSTEM_PROMPT_TEMPLATE = """You are a Worker Bee in the Hive AI orchestration system.

## Your Role
You execute exactly one task. You must:
1. Read the task briefing carefully
2. Execute ONLY the work described in your task
3. Self-verify against all exit criteria before finishing
4. Write your handover memo to the specified JSON path
5. Stop after writing the handover memo

## Rules
- Do NOT start other tasks beyond what's listed
- Do NOT make architectural decisions - flag deviations instead
- Do NOT skip the handover memo - it is required
- Work only within the project directory

## Commit Author Rule
{hive_rules}
"""

HANDOVER_SCHEMA = """{
  "task_id": "...",
  "worker_session_id": "...",
  "completed_at": "ISO8601",
  "files_changed": ["list", "of", "relative/paths"],
  "key_decisions": ["decision 1", "decision 2"],
  "deviations_from_plan": ["deviation 1"],
  "exit_criteria_results": [
    {"criterion": "...", "met": true, "evidence": "..."}
  ],
  "notes_for_next_tasks": "Free-form advice for dependent tasks",
  "cost_usd": 0.0,
  "duration_seconds": 0.0,
  "success": true,
  "error_message": null
}"""


class PromptBuilder:
    def __init__(self, hive_dir: HiveDir):
        self.hd = hive_dir

    def build_context(self, task: Task, all_tasks: dict[str, Task]) -> WorkerContext:
        chapter_contents = {
            fn: self.hd.read_chapter(fn)
            for fn in task.plan_chapters
        }
        recent_handovers = self.hd.load_recent_handovers(task.depends_on)

        return WorkerContext(
            task=task,
            plan_index_content=self.hd.read_plan_index(),
            chapter_contents=chapter_contents,
            l3_state=self.hd.read_l3_state(),
            recent_handovers=recent_handovers,
            hive_rules=self.hd.read_claude_md(),
        )

    def build_system_prompt(self, ctx: WorkerContext) -> str:
        return WORKER_SYSTEM_PROMPT_TEMPLATE.format(
            hive_rules=ctx.hive_rules or "No special rules."
        )

    def build_user_prompt(self, ctx: WorkerContext) -> str:
        task = ctx.task
        handover_path = str(
            self.hd.handover_json_path(task.id).relative_to(self.hd.project_root)
        )

        sections = [
            "# Worker Briefing",
            "",
            f"## Your Task",
            f"**ID**: {task.id}",
            f"**Title**: {task.title}",
            f"**Retry**: {task.retry_count}/{task.max_retries}" if task.retry_count else "",
            "",
            "## Description",
            task.description,
            "",
            "## Exit Criteria (you must verify ALL of these)",
            "",
        ]

        for criterion in task.exit_criteria:
            sections.append(f"- [ ] {criterion}")

        sections += ["", "## Plan Index", "", ctx.plan_index_content]

        if ctx.chapter_contents:
            sections += ["", "## Relevant Plan Chapters", ""]
            for filename, content in ctx.chapter_contents.items():
                sections += [f"### {filename}", "", content, ""]

        if ctx.recent_handovers:
            sections += ["", "## Handovers from Dependency Tasks", ""]
            for memo_text in ctx.recent_handovers:
                sections += [memo_text, "---", ""]

        if ctx.l3_state:
            sections += ["", "## Current Project State", "", ctx.l3_state[:3000]]

        if task.blocked_reason and task.retry_count > 0:
            sections += [
                "",
                "## Previous Failure (this is a retry)",
                "",
                f"Previous attempt failed: {task.blocked_reason}",
                "Please take a different approach.",
            ]

        sections += [
            "",
            "## Handover Memo Instructions",
            "",
            f"When done, write your handover memo as JSON to: `{handover_path}`",
            "",
            "Use this exact schema:",
            "```json",
            HANDOVER_SCHEMA,
            "```",
            "",
            "**Important**: Write the handover memo as the LAST action before stopping.",
        ]

        return "\n".join(s for s in sections if s is not None)
