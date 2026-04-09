"""TaskStateMachine: validates and executes task state transitions."""

from __future__ import annotations

from datetime import datetime, timezone

from hive.hive_dir import HiveDir
from hive.models.task import Task, TaskStatus


class InvalidTransition(Exception):
    pass


VALID_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
    TaskStatus.QUEUE: [TaskStatus.ACTIVE],
    TaskStatus.ACTIVE: [TaskStatus.DONE, TaskStatus.BLOCKED, TaskStatus.QUEUE],
    TaskStatus.BLOCKED: [TaskStatus.QUEUE],
    TaskStatus.DONE: [],
}


class TaskStateMachine:
    def transition(
        self,
        hive_dir: HiveDir,
        task: Task,
        new_status: TaskStatus,
        reason: str = "",
    ) -> Task:
        if new_status not in VALID_TRANSITIONS[task.status]:
            raise InvalidTransition(
                f"Cannot transition {task.id}: {task.status} → {new_status}"
            )

        now = datetime.now(timezone.utc).isoformat()

        if new_status == TaskStatus.ACTIVE:
            task.started_at = now
        elif new_status == TaskStatus.DONE:
            task.completed_at = now
        elif new_status == TaskStatus.BLOCKED:
            task.blocked_reason = reason
        elif new_status == TaskStatus.QUEUE and reason:
            task.blocked_reason = None

        return hive_dir.move_task(task, new_status)
