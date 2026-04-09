"""L3Writer: maintains the global project state document."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from hive.hive_dir import HiveDir
from hive.models.handover import HandoverMemo
from hive.models.task import Task, TaskStatus


COMPACTION_THRESHOLD = 40   # compact after this many completion entries
MAX_L3_TOKENS_ESTIMATE = 4000  # characters (rough token proxy)


class L3Writer:
    def __init__(self, hive_dir: HiveDir, project_root: Path):
        self.hd = hive_dir
        self.project_root = project_root

    def initialize(self, requirement: str, plan_title: str, total_tasks: int) -> None:
        content = f"""# Global Project State

**Requirement**: {requirement}
**Plan**: {plan_title}
**Total Tasks**: {total_tasks}
**Status**: In Progress

---

"""
        self.hd.write_l3_state(content)

    def update(self, task: Task, memo: HandoverMemo, all_tasks: dict[str, Task]) -> None:
        current = self.hd.read_l3_state()
        stats = self._compute_stats(all_tasks)
        files_preview = ", ".join(memo.files_changed[:5])
        if len(memo.files_changed) > 5:
            files_preview += f" (+{len(memo.files_changed) - 5} more)"

        update = (
            f"\n## Completed: {task.title} ({task.completed_at})\n"
            f"**Progress**: {stats['done']}/{stats['total']} tasks "
            f"({stats['pct']:.0f}%)\n"
            f"**Files**: {files_preview or 'none'}\n"
            f"**Notes**: {memo.notes_for_next_tasks[:300]}\n"
        )

        completion_count = current.count("## Completed:")
        if completion_count >= COMPACTION_THRESHOLD:
            # Compact synchronously (blocking is acceptable here - rare operation)
            current = self._compact_sync(current)

        self.hd.write_l3_state(current + update)

    def _compute_stats(self, tasks: dict[str, Task]) -> dict:
        total = len(tasks)
        done = sum(1 for t in tasks.values() if t.status == TaskStatus.DONE)
        blocked = sum(1 for t in tasks.values() if t.status == TaskStatus.BLOCKED)
        pct = (done / total * 100) if total else 0
        return {"total": total, "done": done, "blocked": blocked, "pct": pct}

    def _compact_sync(self, content: str) -> str:
        """Summarize old content using Claude when it gets too long."""
        import subprocess
        prompt = (
            f"Summarize this project state log into a compact markdown document "
            f"under 1000 words, preserving key decisions and current status:\n\n{content}"
        )
        try:
            result = subprocess.run(
                ["claude", "-p", prompt, "--output-format", "json",
                 "--permission-mode", "default", "--max-budget-usd", "0.25"],
                capture_output=True, text=True, timeout=60,
                cwd=str(self.project_root),
            )
            data = json.loads(result.stdout)
            if not data.get("is_error"):
                return f"# Global Project State (Compacted)\n\n{data['result']}\n\n---\n\n"
        except Exception:
            pass
        # Fallback: keep only header + last portion
        lines = content.split("\n")
        header_end = next(
            (i for i, l in enumerate(lines) if l.startswith("## Completed:")), 20
        )
        header = "\n".join(lines[:header_end])
        tail = "\n".join(lines[-60:])
        return f"{header}\n\n[...earlier history compacted...]\n\n{tail}\n"
