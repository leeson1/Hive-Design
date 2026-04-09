from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PlanChapter:
    filename: str
    title: str
    summary: str
    tags: list[str]
    content: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PlanChapter":
        return cls(**d)


@dataclass
class Plan:
    title: str
    original_requirement: str
    chapters: list[PlanChapter]
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Plan":
        d = dict(d)
        d["chapters"] = [PlanChapter.from_dict(c) for c in d.get("chapters", [])]
        return cls(**d)

    def to_index_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"**Requirement**: {self.original_requirement}",
            f"**Created**: {self.created_at}",
            "",
            "## Chapters",
            "",
            "| # | File | Title | Summary | Tags |",
            "|---|------|-------|---------|------|",
        ]
        for i, ch in enumerate(self.chapters, 1):
            tags = ", ".join(ch.tags)
            lines.append(f"| {i} | {ch.filename} | {ch.title} | {ch.summary} | {tags} |")
        return "\n".join(lines) + "\n"
