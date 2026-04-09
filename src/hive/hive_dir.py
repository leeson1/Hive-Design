"""HiveDir: central filesystem abstraction for the .hive/ directory."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from hive.models.task import Task, TaskStatus
from hive.models.handover import HandoverMemo
from hive.models.plan import Plan


class HiveDir:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.root = project_root / ".hive"

    # ── Path properties ────────────────────────────────────────────────────────

    @property
    def plan_dir(self) -> Path:
        return self.root / "plan"

    @property
    def plan_index(self) -> Path:
        return self.plan_dir / "index.md"

    @property
    def chapters_dir(self) -> Path:
        return self.plan_dir / "chapters"

    def chapter_path(self, filename: str) -> Path:
        return self.chapters_dir / filename

    def task_path(self, task_id: str, status: TaskStatus) -> Path:
        return self.root / "tasks" / status.value / f"{task_id}.json"

    @property
    def handovers_dir(self) -> Path:
        return self.root / "handovers"

    def handover_json_path(self, task_id: str) -> Path:
        return self.handovers_dir / f"{task_id}.json"

    def handover_md_path(self, task_id: str) -> Path:
        return self.handovers_dir / f"{task_id}.md"

    @property
    def l2_dir(self) -> Path:
        return self.root / "memory" / "l2"

    def l2_path(self, task_id: str) -> Path:
        return self.l2_dir / f"{task_id}.md"

    @property
    def l3_global(self) -> Path:
        return self.root / "memory" / "l3" / "global.md"

    @property
    def pending_dir(self) -> Path:
        return self.root / "pending"

    # ── Initialization ─────────────────────────────────────────────────────────

    def initialize(self) -> None:
        """Create the full .hive/ directory tree."""
        dirs = [
            self.plan_dir,
            self.chapters_dir,
            self.root / "tasks" / "queue",
            self.root / "tasks" / "active",
            self.root / "tasks" / "done",
            self.root / "tasks" / "blocked",
            self.handovers_dir,
            self.l2_dir,
            self.root / "memory" / "l3",
            self.pending_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    # ── Task operations ────────────────────────────────────────────────────────

    def save_task(self, task: Task) -> None:
        path = self.task_path(task.id, task.status)
        path.write_text(task.to_json())

    def load_task(self, task_id: str) -> Optional[Task]:
        for status in TaskStatus:
            path = self.task_path(task_id, status)
            if path.exists():
                return Task.from_json(path.read_text())
        return None

    def move_task(self, task: Task, new_status: TaskStatus) -> Task:
        """Atomic status transition via os.rename()."""
        old_path = self.task_path(task.id, task.status)
        task.status = new_status
        new_path = self.task_path(task.id, new_status)
        if old_path.exists():
            os.rename(old_path, new_path)
        else:
            self.save_task(task)
        return task

    def load_all_tasks(self) -> dict[str, Task]:
        tasks: dict[str, Task] = {}
        for status in TaskStatus:
            status_dir = self.root / "tasks" / status.value
            if not status_dir.exists():
                continue
            for path in status_dir.glob("*.json"):
                try:
                    task = Task.from_json(path.read_text())
                    tasks[task.id] = task
                except Exception:
                    pass
        return tasks

    # ── Plan operations ────────────────────────────────────────────────────────

    def save_plan(self, plan: Plan) -> None:
        self.plan_index.write_text(plan.to_index_markdown())
        for ch in plan.chapters:
            self.chapter_path(ch.filename).write_text(ch.content)

    def read_plan_index(self) -> str:
        if self.plan_index.exists():
            return self.plan_index.read_text()
        return ""

    def read_chapter(self, filename: str) -> str:
        path = self.chapter_path(filename)
        if path.exists():
            return path.read_text()
        return f"[Chapter not found: {filename}]"

    # ── Handover operations ───────────────────────────────────────────────────

    def save_handover(self, memo: HandoverMemo) -> None:
        self.handover_json_path(memo.task_id).write_text(memo.to_json())
        self.handover_md_path(memo.task_id).write_text(memo.to_markdown())

    def load_handover(self, task_id: str) -> Optional[HandoverMemo]:
        path = self.handover_json_path(task_id)
        if path.exists():
            try:
                return HandoverMemo.from_json(path.read_text())
            except Exception:
                return None
        return None

    def load_recent_handovers(self, task_ids: list[str]) -> list[str]:
        """Load handover markdown for a list of task IDs (dependency handovers)."""
        results = []
        for tid in task_ids:
            path = self.handover_md_path(tid)
            if path.exists():
                results.append(path.read_text())
        return results

    def load_last_n_handovers(self, n: int = 10) -> list[str]:
        """Load the N most recently written handover memos."""
        paths = sorted(
            self.handovers_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return [p.read_text() for p in paths[:n]]

    # ── Memory operations ──────────────────────────────────────────────────────

    def read_l3_state(self) -> str:
        if self.l3_global.exists():
            return self.l3_global.read_text()
        return ""

    def write_l3_state(self, content: str) -> None:
        self.l3_global.parent.mkdir(parents=True, exist_ok=True)
        self.l3_global.write_text(content)

    # ── Project CLAUDE.md ──────────────────────────────────────────────────────

    def read_claude_md(self) -> str:
        path = self.project_root / "CLAUDE.md"
        if path.exists():
            return path.read_text()
        return ""

    # ── Pending issues ─────────────────────────────────────────────────────────

    def write_pending(self, task_id: str, reason: str) -> None:
        path = self.pending_dir / f"{task_id}.md"
        path.write_text(f"# Pending Decision: {task_id}\n\n{reason}\n")
