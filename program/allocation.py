from __future__ import annotations

import math
import random
import statistics
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from transport_lib import transport


Number = float
Agent  = Dict[str, Any]
Task   = Dict[str, Any]


# ──────────────────────────────────────────────────────────
#  Validare
# ──────────────────────────────────────────────────────────
def validate_problem(agents, tasks, cost_matrix):
    errors = []
    if not agents:      errors.append("Agents list is empty")
    if not tasks:       errors.append("Tasks list is empty")
    if not cost_matrix: errors.append("Cost matrix is empty"); return errors
    if len(cost_matrix) != len(agents):
        errors.append("Cost matrix rows must match agents count")
    for row in cost_matrix:
        if len(row) != len(tasks):
            errors.append("Each cost matrix row must match tasks count"); break
    for a in agents:
        if "capacity" not in a: errors.append("Agent missing capacity"); break
    for t in tasks:
        if "volume"   not in t: errors.append("Task missing volume");    break
    return errors


# ──────────────────────────────────────────────────────────
#  Normaliz & balans (intern)
# ──────────────────────────────────────────────────────────
def _normalize_problem(agents, tasks, cost_matrix):
    na = [{"id": a.get("id", f"A{i+1}"), "name": a.get("name", f"Agent {i+1}"),
           "capacity": float(a["capacity"])} for i, a in enumerate(agents)]
    nt = [{"id": t.get("id", f"T{j+1}"), "name": t.get("name", f"Queue {j+1}"),
           "volume": float(t["volume"])}   for j, t in enumerate(tasks)]
    nc = [[float(v) for v in row] for row in cost_matrix]
    return na, nt, nc


def _balance_problem(agents, tasks, cost_matrix):
    supply = [a["capacity"] for a in agents]
    demand = [t["volume"]   for t in tasks]
    ts = sum(supply); td = sum(demand)

    ab = [dict(a) for a in agents]
    tb = [dict(t) for t in tasks]
    cb = [row[:] for row in cost_matrix]
    m0, n0 = len(agents), len(tasks)

    if ts > td:
        diff = ts - td
        tb.append({"id": f"T{n0+1}", "name": "Queue Fictive", "volume": diff, "fictive": True})
        for row in cb: row.append(0.0)
    elif td > ts:
        diff = td - ts
        ab.append({"id": f"A{m0+1}", "name": "Agent Fictiv", "capacity": diff, "fictive": True})
        cb.append([0.0] * len(tb))

    return ab, tb, cb, m0, n0


def _compute_cost(allocation, cost_matrix):
    return sum(allocation[i][j] * cost_matrix[i][j]
               for i in range(len(allocation))
               for j in range(len(allocation[i])))


# ──────────────────────────────────────────────────────────
#  Alocare aleatoare
# ──────────────────────────────────────────────────────────
def _random_allocation_single(supply, demand):
    m, n = len(supply), len(demand)
    rs, rd = supply[:], demand[:]
    alloc = [[0.0]*n for _ in range(m)]
    for i in range(m - 1):
        for j in range(n - 1):
            mx = min(rs[i], rd[j])
            mn = max(0.0, rs[i] - sum(rd[j+1:]))
            if mx < mn: mn = mx
            v = mn + (mx - mn) * random.random()
            alloc[i][j] = v; rs[i] -= v; rd[j] -= v
        alloc[i][n-1] = rs[i]; rd[n-1] -= rs[i]; rs[i] = 0.0
    for j in range(n):
        alloc[m-1][j] = rd[j]; rs[m-1] -= rd[j]; rd[j] = 0.0
    return alloc


def random_allocation_stats(agents, tasks, cost_matrix, runs=100):
    agents, tasks, cost_matrix = _normalize_problem(agents, tasks, cost_matrix)
    ab, tb, cb, m0, n0 = _balance_problem(agents, tasks, cost_matrix)
    supply = [a["capacity"] for a in ab]
    demand = [t["volume"]   for t in tb]

    costs, sample = [], []
    for idx in range(runs):
        alloc = _random_allocation_single(supply[:], demand[:])
        cost  = _compute_cost(alloc, cb)
        costs.append(cost)
        if idx == 0: sample = alloc

    trimmed = [row[:n0] for row in sample[:m0]]
    return {
        "avg_cost":          round(statistics.mean(costs), 4),
        "std_dev":           round(statistics.pstdev(costs), 4),
        "sample_allocation": trimmed,
    }


# ──────────────────────────────────────────────────────────
#  Rezolvare cu Metoda Potentialelor (MODI)  — via transport.py
# ──────────────────────────────────────────────────────────
def _solve_with_modi(supply, demand, cost_matrix):
    """
    Apeleaza rezolva_transport() din transport.py, care implementeaza:
      1. Metoda Coltului N-V  (solutie initiala)
      2. Metoda Potentialelor / MODI  (optimizare iterativa)
    Returneaza structura compatibila cu restul aplicatiei.
    """
    result = transport.rezolva_transport(supply, demand, cost_matrix)

    if result["status"] != "optimal":
        return {
            "status": "error",
            "allocation": [[0.0]*len(demand) for _ in range(len(supply))],
            "iterations": 0,
            "total_cost": 0.0,
            "iterations_visual": [],
        }

    m = result["m_orig"]
    n = result["n_orig"]
    x_opt = result["x_opt"]

    allocation = [[float(x_opt[i][j]) for j in range(n)] for i in range(m)]

    # nr iteratii = cate snapshot-uri exista dupa cea initiala
    iters = max(0, len(result["iterations"]) - 1)

    visuals = _build_modi_visual(result)

    return {
        "status":            "optimal",
        "allocation":        allocation,
        "iterations":        iters,
        "total_cost":        float(result["f_opt"]),
        "iterations_visual": visuals,
    }


def optimal_allocation(agents, tasks, cost_matrix):
    agents, tasks, cost_matrix = _normalize_problem(agents, tasks, cost_matrix)
    ab, tb, cb, m0, n0 = _balance_problem(agents, tasks, cost_matrix)

    supply = [a["capacity"] for a in ab]
    demand = [t["volume"]   for t in tb]

    result = _solve_with_modi(supply, demand, cb)

    trimmed = [row[:n0] for row in result["allocation"][:m0]]
    total_cost = _compute_cost(trimmed, cost_matrix)

    return {
        "total_cost":        round(total_cost, 4),
        "allocation":        trimmed,
        "iterations":        result["iterations"],
        "iterations_visual": result["iterations_visual"],
        "is_optimal":        result["status"] == "optimal",
    }


# ──────────────────────────────────────────────────────────
#  Construieste vizualizarea iteratiilor MODI
#  Fiecare snapshot contine: x, c, J, u, v, delta, circuit, pq, theta
# ──────────────────────────────────────────────────────────
def _fmt(v):
    """Formateaza un numar (Fraction sau float) ca string compact."""
    try:
        f = transport.F(v)
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"
    except Exception:
        return str(v)


def _build_modi_visual(result):
    """
    Construieste lista de string-uri (cate unul per iteratie)
    in formatul pe care parserul JS il asteapta:

    ITERATIA  I_<k>
    Pivot: linie=R coloana=C P=val   (sau 'fara pivot')
    u: u1=... u2=... ...
    v: v1=... v2=... ...
    TABEL x / delta:
    <m linii: CB  xij_name  xb_value  val0 val1 ...>
    z_j ->  v1  v2  ...
    Δ_j ->  d(i,j) ...
    -> Intra in baza: x<p+1><q+1>
    -> Iese din baza: x<ie+1><je+1>
    """
    snaps = result["iterations"]
    m_orig = result["m_orig"]
    n_orig = result["n_orig"]
    m = result["m"]
    n = result["n"]
    fictiva_sursa = result.get("fictiva_sursa", False)
    fictiva_dest  = result.get("fictiva_dest",  False)

    visuals = []

    for snap in snaps:
        k       = snap["k"]
        x       = snap["x"]
        c       = snap["c"]
        J       = set(tuple(cell) for cell in snap["J"])
        u       = snap["u"]
        v       = snap["v"]
        delta   = snap["delta"]   # dict {(i,j): val} sau None
        circuit = snap["circuit"]
        pq      = snap["pq"]
        theta   = snap["theta"]
        status  = snap["status"]
        msg     = snap["msg"]
        fk      = snap["fk"]

        lines = []
        lines.append(f"ITERATIA  I_{k}")
        lines.append("=" * 60)

        # Pivot
        if pq is not None:
            pr, pc = pq
            try:
                pval = _fmt(x[pr][pc]) if x else "?"
            except Exception:
                pval = "?"
            lines.append(f"Pivot: linie={pr+1} coloana={pc+1} P={pval}")
        else:
            lines.append("fara pivot")

        lines.append(f"Cost curent: {_fmt(fk)}")
        lines.append("")

        # Multiplicatori u, v
        if u is not None:
            u_str = "  ".join(f"u{i+1}={_fmt(u[i])}" for i in range(len(u)))
            v_str = "  ".join(f"v{j+1}={_fmt(v[j])}" for j in range(len(v)))
            lines.append(f"u: {u_str}")
            lines.append(f"v: {v_str}")
            lines.append("")

        # Tabel MODI — afisam liniile bazice
        # Formatul cerut de parser: CB  baseName  xb  val0 val1 ...
        # Folosim: CB = c[i][j_bazic_pe_linia_i], base = x<i+1><j+1>, xb = x[i][j]
        # Dar pentru MODI e mai natural sa afisam TOATA linia i a matricei x

        # c_j header (valorile costurilor pe coloana j)
        cj_vals = "  ".join(_fmt(c[0][j]) for j in range(n)) if c else ""
        lines.append(f"c_j ->  {cj_vals}")

        # Var names header
        var_names = [f"x{i+1}{j+1}" for i in range(m) for j in range(n)]
        # Folosim x<row><col> per coloana, deci header coloane
        col_names = "  ".join(f"x{i+1}{j+1}" for i in range(m) for j in range(n))
        # Simplificat: afisam coloane ca B1..Bn
        col_header = "  ".join(f"B{j+1}" for j in range(n))
        lines.append(f"       {col_header}")
        lines.append("")

        for i in range(m):
            # Gasim celula bazica cu val maxima pe linia i (pentru CB)
            bazice_i = [(i, j) for (bi, j) in J if bi == i]
            if bazice_i:
                cb_val = _fmt(c[i][bazice_i[0][1]])
                base_name = f"x{i+1}{bazice_i[0][1]+1}"
                xb_val    = _fmt(x[i][bazice_i[0][1]])
            else:
                cb_val    = "0"
                base_name = f"A{i+1}"
                xb_val    = "0"

            row_vals = "  ".join(_fmt(x[i][j]) for j in range(n))
            lines.append(f"{cb_val}  {base_name}  {xb_val}  {row_vals}")

        lines.append("")

        # z_j = v[j] (multiplicatorii destinatie)
        if v is not None:
            zj_str = "  ".join(_fmt(v[j]) for j in range(n))
            lines.append(f"z_j ->  {zj_str}")

        # delta_j — pentru nebazice
        if delta is not None:
            delta_row = []
            for j in range(n):
                # afisam delta celei mai reprezentative celule nebazice din coloana j
                vals = [delta.get((i, j), None) for i in range(m) if (i, j) not in J]
                best = next((d for d in vals if d is not None), None)
                delta_row.append(_fmt(best) if best is not None else "·")
            lines.append(f"Δ_j ->  {'  '.join(delta_row)}")

        # Circuit
        if circuit is not None and pq is not None:
            p_, q_ = pq
            lines.append(f"-> Intra in baza: x{p_+1}{q_+1}")
            if circuit and len(circuit) >= 3:
                # celula iesita = primul rang impar al circuitului
                out_cell = circuit[1]
                oi, oj = out_cell
                lines.append(f"-> Iese din baza: x{oi+1}{oj+1}")
            lines.append(f"-> theta = {_fmt(theta)}")

        if status == "optimal":
            lines.append("")
            lines.append("✓ Toate delta[i][j] >= 0  =>  Solutia este OPTIMA")

        visuals.append("\n".join(lines))

    return visuals


# ──────────────────────────────────────────────────────────
#  Graf
# ──────────────────────────────────────────────────────────
def build_graph_data(agents, tasks, allocation, cost_matrix):
    nodes, edges = [], []
    for t in tasks:
        nodes.append({"id": t["id"], "label": t["name"], "type": "task",  "value": t["volume"]})
    for a in agents:
        nodes.append({"id": a["id"], "label": a["name"], "type": "agent", "value": a["capacity"]})
    for i, task in enumerate(tasks):
        for j, agent in enumerate(agents):
            flow = allocation[j][i]
            edges.append({"source": task["id"], "target": agent["id"],
                          "flow": flow, "cost": cost_matrix[j][i],
                          "total": flow * cost_matrix[j][i]})
    return {"nodes": nodes, "edges": edges}


# ──────────────────────────────────────────────────────────
#  Comparare
# ──────────────────────────────────────────────────────────
def compare_allocations(agents, tasks, cost_matrix):
    agents_n, tasks_n, costs_n = _normalize_problem(agents, tasks, cost_matrix)

    rand_result = random_allocation_stats(agents_n, tasks_n, costs_n, runs=100)
    opt_result  = optimal_allocation(agents_n, tasks_n, costs_n)

    savings_pct = 0.0
    if rand_result["avg_cost"] > 0:
        savings_pct = (rand_result["avg_cost"] - opt_result["total_cost"]) / rand_result["avg_cost"] * 100.0

    graph = build_graph_data(agents_n, tasks_n, opt_result["allocation"], costs_n)

    return {
        "random":       rand_result,
        "optimal":      opt_result,
        "savings_pct":  round(savings_pct, 2),
        "graph":        graph,
    }
