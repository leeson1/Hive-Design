import re
import time


def make_task_id(index: int, title: str) -> str:
    """Generate a stable, human-readable task ID."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")[:40]
    return f"task-{index:03d}-{slug}"
