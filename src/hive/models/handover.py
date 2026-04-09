from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ExitCriterionResult:
    criterion: str
    met: bool
    evidence: str = ""


@dataclass
class HandoverMemo:
    task_id: str
    worker_session_id: str
    completed_at: str
    files_changed: list[str]
    key_decisions: list[str]
    deviations_from_plan: list[str]
    exit_criteria_results: list[ExitCriterionResult]
    notes_for_next_tasks: str
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "HandoverMemo":
        d = dict(d)
        d["exit_criteria_results"] = [
            ExitCriterionResult(**r) if isinstance(r, dict) else r
            for r in d.get("exit_criteria_results", [])
        ]
        return cls(**d)

    @classmethod
    def from_json(cls, text: str) -> "HandoverMemo":
        return cls.from_dict(json.loads(text))

    def to_markdown(self) -> str:
        lines = [
            f"# Handover Memo: {self.task_id}",
            "",
            f"**Completed**: {self.completed_at}",
            f"**Worker Session**: {self.worker_session_id}",
            f"**Duration**: {self.duration_seconds:.1f}s",
            f"**Cost**: ${self.cost_usd:.4f}",
            f"**Success**: {'Yes' if self.success else 'No'}",
            "",
            "## Files Changed",
            "",
        ]
        for f in self.files_changed:
            lines.append(f"- `{f}`")

        lines += ["", "## Key Decisions", ""]
        for d in self.key_decisions:
            lines.append(f"- {d}")

        lines += ["", "## Deviations from Plan", ""]
        for dev in self.deviations_from_plan:
            lines.append(f"- {dev}")
        if not self.deviations_from_plan:
            lines.append("- None")

        lines += ["", "## Exit Criteria", ""]
        for r in self.exit_criteria_results:
            mark = "x" if r.met else " "
            lines.append(f"- [{mark}] {r.criterion}")
            if r.evidence:
                lines.append(f"  - Evidence: {r.evidence}")

        lines += ["", "## Notes for Next Tasks", "", self.notes_for_next_tasks]
        return "\n".join(lines) + "\n"

    @classmethod
    def synthesize(
        cls,
        task_id: str,
        duration_seconds: float,
        cost_usd: float,
        notes: str = "",
    ) -> "HandoverMemo":
        """Create a minimal memo when worker didn't write one explicitly."""
        return cls(
            task_id=task_id,
            worker_session_id="unknown",
            completed_at=datetime.now(timezone.utc).isoformat(),
            files_changed=[],
            key_decisions=[],
            deviations_from_plan=[],
            exit_criteria_results=[],
            notes_for_next_tasks=notes or "Worker completed without writing explicit handover.",
            cost_usd=cost_usd,
            duration_seconds=duration_seconds,
        )
