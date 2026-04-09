"""L2Writer: writes per-task summary files after task completion."""

from __future__ import annotations

from hive.hive_dir import HiveDir
from hive.models.handover import HandoverMemo
from hive.models.task import Task


class L2Writer:
    def __init__(self, hive_dir: HiveDir):
        self.hd = hive_dir

    def write(self, task: Task, memo: HandoverMemo) -> None:
        lines = [
            f"# L2 Summary: {task.title}",
            "",
            f"**Task ID**: {task.id}",
            f"**Completed**: {task.completed_at}",
            f"**Cost**: ${memo.cost_usd:.4f}",
            "",
            "## What Was Done",
            "",
            memo.notes_for_next_tasks,
            "",
            "## Files Changed",
            "",
        ]
        for f in memo.files_changed:
            lines.append(f"- `{f}`")

        lines += ["", "## Key Decisions", ""]
        for d in memo.key_decisions:
            lines.append(f"- {d}")

        lines += ["", "## Deviations from Plan", ""]
        for dev in memo.deviations_from_plan:
            lines.append(f"- {dev}")
        if not memo.deviations_from_plan:
            lines.append("- None")

        self.hd.l2_path(task.id).write_text("\n".join(lines) + "\n")
