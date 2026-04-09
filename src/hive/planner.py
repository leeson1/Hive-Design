"""Planner: Phase 1 AI-driven plan generation."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from hive.hive_dir import HiveDir
from hive.memory.l3_writer import L3Writer
from hive.models.plan import Plan, PlanChapter
from hive.models.task import Task, TaskPriority
from hive.utils.ids import make_task_id


class PlannerError(Exception):
    pass


PLANNER_SYSTEM_PROMPT = """You are the Hive Planner. Your job is to take a software requirement
and produce a structured plan with chapters and executable tasks.

Output a single JSON object with this exact structure:
{
  "title": "Plan title",
  "chapters": [
    {
      "filename": "01-overview.md",
      "title": "Project Overview",
      "summary": "1-2 sentence abstract",
      "tags": ["overview", "architecture"],
      "content": "Full markdown content of this chapter"
    }
  ],
  "tasks": [
    {
      "title": "Short task title",
      "description": "Detailed description of what to implement",
      "plan_chapters": ["01-overview.md"],
      "exit_criteria": [
        "Tests pass",
        "Feature X works as described"
      ],
      "depends_on": [],
      "priority": 2
    }
  ]
}

Rules:
- Tasks must be small and focused (1-4 hours of work each)
- Exit criteria must be concrete and verifiable
- Dependencies must be task indices (0-based) that will become IDs
- Chapters should be self-contained and readable independently
- Priority: 0=critical, 1=high, 2=normal, 3=low
"""


class Planner:
    def __init__(self, hive_dir: HiveDir, project_root: Path):
        self.hd = hive_dir
        self.project_root = project_root
        self.l3 = L3Writer(hive_dir, project_root)

    async def run(self, requirement: str) -> tuple[Plan, list[Task]]:
        # Scan existing project context for the planner
        context_hint = self._scan_project_context()
        prompt = self._build_prompt(requirement, context_hint)

        raw = await self._run_claude(prompt)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            # Try to extract JSON from mixed text output
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise PlannerError(f"Could not parse planner output as JSON: {e}")

        plan = self._build_plan(data, requirement)
        tasks = self._build_tasks(data, plan)

        # Write to .hive/
        self.hd.save_plan(plan)
        for task in tasks:
            self.hd.save_task(task)

        # Initialize L3
        self.l3.initialize(requirement, plan.title, len(tasks))

        return plan, tasks

    def _build_plan(self, data: dict, requirement: str) -> Plan:
        chapters = [
            PlanChapter(
                filename=ch["filename"],
                title=ch["title"],
                summary=ch["summary"],
                tags=ch.get("tags", []),
                content=ch.get("content", ""),
            )
            for ch in data.get("chapters", [])
        ]
        return Plan(
            title=data.get("title", "Untitled Plan"),
            original_requirement=requirement,
            chapters=chapters,
        )

    def _build_tasks(self, data: dict, plan: Plan) -> list[Task]:
        raw_tasks = data.get("tasks", [])
        tasks: list[Task] = []
        id_map: dict[int, str] = {}

        for i, td in enumerate(raw_tasks):
            task_id = make_task_id(i + 1, td.get("title", f"task-{i+1}"))
            id_map[i] = task_id

            # Resolve dependency indices to IDs
            depends_on = []
            for dep in td.get("depends_on", []):
                if isinstance(dep, int) and dep in id_map:
                    depends_on.append(id_map[dep])
                elif isinstance(dep, str):
                    depends_on.append(dep)

            task = Task(
                id=task_id,
                title=td.get("title", "Untitled Task"),
                description=td.get("description", ""),
                plan_chapters=td.get("plan_chapters", []),
                exit_criteria=td.get("exit_criteria", []),
                depends_on=depends_on,
                priority=TaskPriority(td.get("priority", TaskPriority.NORMAL.value)),
            )
            tasks.append(task)

        return tasks

    def _scan_project_context(self) -> str:
        """Gather brief context about the existing project."""
        hints = []
        readme = self.project_root / "README.md"
        if readme.exists():
            hints.append(f"Existing README:\n{readme.read_text()[:1000]}")

        # List top-level files/dirs
        items = [p.name for p in self.project_root.iterdir()
                 if not p.name.startswith(".")]
        if items:
            hints.append(f"Project contains: {', '.join(sorted(items))}")

        return "\n\n".join(hints) if hints else "Empty project directory."

    def _build_prompt(self, requirement: str, context_hint: str) -> str:
        return (
            f"Create a detailed plan for the following software requirement.\n\n"
            f"## Requirement\n{requirement}\n\n"
            f"## Existing Project Context\n{context_hint}\n\n"
            f"Produce a complete plan with chapters and tasks as specified."
        )

    async def _run_claude(self, prompt: str) -> str:
        cmd = [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--system-prompt", PLANNER_SYSTEM_PROMPT,
            "--permission-mode", "default",
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.project_root),
        )
        stdout, stderr = await proc.communicate()

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            raise PlannerError(
                f"Claude returned non-JSON output.\nstdout: {stdout.decode()[:500]}\n"
                f"stderr: {stderr.decode()[:300]}"
            )

        if data.get("is_error"):
            raise PlannerError(f"Claude error: {data.get('result', 'unknown')}")

        return data["result"]
