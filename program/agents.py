from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Agent:
    id: str
    name: str
    capacity: float


def build_agents(agents: List[dict]) -> List[Agent]:
    return [Agent(id=a["id"], name=a["name"], capacity=float(a["capacity"])) for a in agents]
