from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    QUEUE = "queue"
    ACTIVE = "active"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Task:
    id: str
    title: str
    description: str
    plan_chapters: list[str]
    exit_criteria: list[str]
    depends_on: list[str]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.QUEUE
    assigned_worker: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    handover_path: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
    blocked_reason: Optional[str] = None

    def to_json(self) -> str:
        d = dataclasses.asdict(self)
        d["status"] = self.status.value
        d["priority"] = self.priority.value
        return json.dumps(d, indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        d = dict(d)
        d["status"] = TaskStatus(d["status"])
        d["priority"] = TaskPriority(d.get("priority", TaskPriority.NORMAL.value))
        return cls(**d)

    @classmethod
    def from_json(cls, text: str) -> "Task":
        return cls.from_dict(json.loads(text))
