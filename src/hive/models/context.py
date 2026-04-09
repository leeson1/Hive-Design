from __future__ import annotations

from dataclasses import dataclass, field

from hive.models.task import Task


@dataclass
class WorkerContext:
    task: Task
    plan_index_content: str
    chapter_contents: dict[str, str]
    l3_state: str
    recent_handovers: list[str]
    hive_rules: str


@dataclass
class DroneContext:
    plan_index: str
    global_state: str
    recent_handovers: list[str]
    all_tasks: dict[str, Task]
