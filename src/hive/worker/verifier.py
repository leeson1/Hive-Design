"""WorkerVerifier: validates exit criteria and handover memo after worker completes."""

from __future__ import annotations

from dataclasses import dataclass

from hive.hive_dir import HiveDir
from hive.models.handover import HandoverMemo
from hive.models.task import Task


@dataclass
class VerificationResult:
    all_met: bool
    unmet: list[str]
    evidence: dict[str, str]


class WorkerVerifier:
    def __init__(self, hive_dir: HiveDir):
        self.hd = hive_dir

    def load_handover(self, task: Task) -> HandoverMemo | None:
        return self.hd.load_handover(task.id)

    def check_exit_criteria(self, task: Task, memo: HandoverMemo) -> VerificationResult:
        """Check whether all exit criteria are marked as met in the handover memo."""
        met_map: dict[str, bool] = {}
        evidence_map: dict[str, str] = {}

        for r in memo.exit_criteria_results:
            met_map[r.criterion] = r.met
            evidence_map[r.criterion] = r.evidence

        unmet = []
        for criterion in task.exit_criteria:
            if not met_map.get(criterion, False):
                unmet.append(criterion)

        return VerificationResult(
            all_met=len(unmet) == 0,
            unmet=unmet,
            evidence=evidence_map,
        )

    def synthesize_memo(
        self, task: Task, claude_result: dict, duration_seconds: float
    ) -> HandoverMemo:
        """Create a minimal memo from Claude's raw output when worker didn't write one."""
        cost = claude_result.get("total_cost_usd", 0.0)
        session_id = claude_result.get("session_id", "unknown")
        raw_result = claude_result.get("result", "")

        return HandoverMemo.synthesize(
            task_id=task.id,
            duration_seconds=duration_seconds,
            cost_usd=cost,
            notes=f"Auto-synthesized. Worker output: {raw_result[:500]}",
        )
