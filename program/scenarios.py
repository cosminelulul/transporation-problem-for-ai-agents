from __future__ import annotations

from typing import Any, Dict, List


Scenario = Dict[str, Any]


SCENARIOS: Dict[str, Scenario] = {
    "small": {
        "id": "small",
        "name": "Mic",
        "agents": [
            {"id": "A1", "name": "Alpha", "capacity": 30},
            {"id": "A2", "name": "Beta", "capacity": 25},
            {"id": "A3", "name": "Omega", "capacity": 45},
        ],
        "tasks": [
            {"id": "T1", "name": "NLP", "volume": 20, "type": "Decizie"},
            {"id": "T2", "name": "Computer Vision", "volume": 40, "type": "Decizie"},
            {"id": "T3", "name": "Search", "volume": 40, "type": "Decizie"},
        ],
        "cost_matrix": [
            [4, 6, 9],
            [5, 4, 7],
            [6, 3, 4],
        ],
    },
    "medium": {
        "id": "medium",
        "name": "Mediu",
        "agents": [
            {"id": "A1", "name": "Alpha", "capacity": 25},
            {"id": "A2", "name": "Beta", "capacity": 35},
            {"id": "A3", "name": "Gamma", "capacity": 40},
            {"id": "A4", "name": "Delta", "capacity": 30},
        ],
        "tasks": [
            {"id": "T1", "name": "NLP", "volume": 20, "type": "Decizie"},
            {"id": "T2", "name": "Computer Vision", "volume": 30, "type": "Decizie"},
            {"id": "T3", "name": "Recomandari", "volume": 25, "type": "Decizie"},
            {"id": "T4", "name": "Search", "volume": 25, "type": "Decizie"},
            {"id": "T5", "name": "Dialog", "volume": 30, "type": "Decizie"},
        ],
        "cost_matrix": [
            [6, 7, 5, 8, 6],
            [5, 4, 7, 6, 8],
            [7, 6, 4, 5, 5],
            [8, 5, 6, 4, 7],
        ],
    },
    "large": {
        "id": "large",
        "name": "Mare",
        "agents": [
            {"id": "A1", "name": "Alpha", "capacity": 30},
            {"id": "A2", "name": "Beta", "capacity": 25},
            {"id": "A3", "name": "Gamma", "capacity": 35},
            {"id": "A4", "name": "Delta", "capacity": 20},
            {"id": "A5", "name": "Omega", "capacity": 40},
            {"id": "A6", "name": "Sigma", "capacity": 30},
        ],
        "tasks": [
            {"id": "T1", "name": "NLP", "volume": 20, "type": "Decizie"},
            {"id": "T2", "name": "Computer Vision", "volume": 25, "type": "Decizie"},
            {"id": "T3", "name": "Recomandari", "volume": 30, "type": "Decizie"},
            {"id": "T4", "name": "Search", "volume": 25, "type": "Decizie"},
            {"id": "T5", "name": "Dialog", "volume": 20, "type": "Decizie"},
            {"id": "T6", "name": "Sumarizare", "volume": 35, "type": "Decizie"},
            {"id": "T7", "name": "ETL", "volume": 15, "type": "Decizie"},
            {"id": "T8", "name": "Monitoring", "volume": 10, "type": "Decizie"},
        ],
        "cost_matrix": [
            [7, 6, 8, 9, 5, 6, 7, 8],
            [6, 5, 7, 8, 6, 7, 6, 7],
            [8, 7, 6, 7, 8, 6, 5, 6],
            [9, 6, 7, 6, 7, 8, 6, 5],
            [5, 7, 8, 6, 6, 5, 7, 8],
            [6, 8, 7, 5, 7, 6, 8, 6],
        ],
    },
}


def list_scenarios() -> List[Dict[str, Any]]:
    return [{"id": s["id"], "name": s["name"]} for s in SCENARIOS.values()]


def get_scenario(scenario_id: str) -> Scenario:
    return SCENARIOS.get(scenario_id, SCENARIOS["small"])
