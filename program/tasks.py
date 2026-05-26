from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TaskQueue:
    id: str
    name: str
    volume: float


def build_tasks(tasks: List[dict]) -> List[TaskQueue]:
    return [TaskQueue(id=t["id"], name=t["name"], volume=float(t["volume"])) for t in tasks]
