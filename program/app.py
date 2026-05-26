from __future__ import annotations

from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from allocation import (
    compare_allocations,
    optimal_allocation,
    random_allocation_stats,
    validate_problem,
)
from scenarios import get_scenario, list_scenarios

app = Flask(__name__)

StateType = Dict[str, Any]

current_state: StateType = {
    "agents": [],
    "tasks": [],
    "cost_matrix": [],
}


def _load_initial_state() -> None:
    scenario = get_scenario("small")
    current_state["agents"] = scenario["agents"]
    current_state["tasks"] = scenario["tasks"]
    current_state["cost_matrix"] = scenario["cost_matrix"]


_load_initial_state()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/agents", methods=["GET"])
def api_agents():
    return jsonify(current_state["agents"])


@app.route("/api/tasks", methods=["GET"])
def api_tasks():
    return jsonify(current_state["tasks"])


@app.route("/api/scenarios", methods=["GET"])
def api_scenarios():
    return jsonify(list_scenarios())


@app.route("/api/scenarios/load", methods=["POST"])
def api_load_scenario():
    payload = request.get_json(silent=True) or {}
    scenario_id = payload.get("scenario_id", "small")
    scenario = get_scenario(scenario_id)

    agents = payload.get("agents", scenario["agents"])
    tasks = payload.get("tasks", scenario["tasks"])
    cost_matrix = payload.get("cost_matrix", scenario["cost_matrix"])

    errors = validate_problem(agents, tasks, cost_matrix)
    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    current_state["agents"] = agents
    current_state["tasks"] = tasks
    current_state["cost_matrix"] = cost_matrix

    return jsonify({
        "status": "ok",
        "scenario_id": scenario_id,
        "agents": agents,
        "tasks": tasks,
        "cost_matrix": cost_matrix,
    })


@app.route("/api/cost-matrix", methods=["POST"])
def api_cost_matrix():
    payload = request.get_json(silent=True) or {}
    cost_matrix = payload.get("cost_matrix")
    if cost_matrix is None:
        return jsonify({"status": "error", "errors": ["Missing cost_matrix"]}), 400

    errors = validate_problem(current_state["agents"], current_state["tasks"], cost_matrix)
    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    current_state["cost_matrix"] = cost_matrix
    return jsonify({"status": "ok"})


@app.route("/api/allocate/random", methods=["POST"])
def api_allocate_random():
    result = random_allocation_stats(
        current_state["agents"],
        current_state["tasks"],
        current_state["cost_matrix"],
        runs=100,
    )
    return jsonify(result)


@app.route("/api/allocate/optimal", methods=["POST"])
def api_allocate_optimal():
    result = optimal_allocation(
        current_state["agents"],
        current_state["tasks"],
        current_state["cost_matrix"],
    )
    return jsonify(result)


@app.route("/api/compare", methods=["POST"])
def api_compare():
    result = compare_allocations(
        current_state["agents"],
        current_state["tasks"],
        current_state["cost_matrix"],
    )
    return jsonify(result)


if __name__ == "__main__":
    print("Server pornit la http://127.0.0.1:5000")
    app.run(debug=False)
