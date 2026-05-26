# transporation-problem-for-ai-agents

# Distribuția Task-urilor către Agenți AI într-un Sistem Multi-Agent
# Task Distribution to AI Agents in a Multi-Agent System



> **RO:** Aplicație web interactivă pentru optimizarea alocării task-urilor în sisteme multi-agent, construită pe Problema Transporturilor rezolvată prin **Metoda Colțului Nord-Vest** și **Metoda Potențialelor (MODI)**.
>
> **EN:** Interactive web application for optimizing task allocation in multi-agent systems, built on the Transportation Problem solved via the **North-West Corner Method** and the **MODI / Stepping-Stone Method**.

---

<details open>
<summary><strong>🇷🇴 Română</strong></summary>

## 1. Scopul Proiectului

Proiectul simulează un sistem multi-agent (MAS) în care mai mulți agenți AI specializați procesează task-uri diverse (NLP, Computer Vision, Search, Dialog etc.). Problema centrală: **cum distribui task-urile astfel încât costul total de alocare să fie minim?**

Răspunsul vine din cercetarea operațională: **Problema Transporturilor**. Librăria implementată rezolvă această problemă în două faze:

1. **Metoda Colțului Nord-Vest** — generează o soluție inițială de bază fezabilă
2. **Metoda Potențialelor / MODI** — optimizează iterativ soluția până la optim global

Aplicația demonstrează vizual diferența dintre o distribuție **aleatorie** a task-urilor și cea **optimizată**, cuantificând câștigul în cost și eficiență.

> Proiect realizat în cadrul materiei de **Cercetări Operaționale** la Facultatea de Științe Aplicate, **Universitatea Politehnica din București (UNSTPB)**.

---

## 2. Obiective

- Minimizarea costului total de alocare a task-urilor către agenți AI
- Respectarea constrângerilor de capacitate ale fiecărui agent și a volumului fiecărei cozi de task-uri
- Rezolvare exactă prin Metoda Potențialelor + Colțul Nord-Vest
- Comparație vizuală și numerică față de alocarea aleatorie (100 de simulări Monte Carlo)

---

## 3. Context și Motivație

Un sistem multi-agent (MAS) este o arhitectură software în care agenți autonomi colaborează pentru rezolvarea problemelor complexe. Fiecare agent are specializări, capacitate limitată și un cost diferit pentru fiecare tip de task.

Fără un mecanism de alocare inteligent, task-urile distribuite arbitrar duc la supraîncărcare a unor agenți, subutilizarea altora și costuri nejustificate.

**Problema Transporturilor** modelează exact această situație: agenții sunt sursele cu o ofertă (capacitate), task-urile sunt destinațiile cu o cerere (volum), iar costul transportului unui task de la un agent reprezintă costul de procesare.

---

## 4. Arhitectura Proiectului

```
project_fixed/
│
├── app.py                      # Server Flask (entry point)
├── allocation.py               # Logica de alocare: random, MODI, comparare, graf
├── agents.py                   # Modelul de date Agent
├── tasks.py                    # Modelul de date TaskQueue
├── scenarios.py                # Cele 3 scenarii predefinite (Mic, Mediu, Mare)
│
├── transport_lib/
│   ├── transport.py            # Implementarea algoritmului NV + MODI
│   
│
├── templates/
│   └── index.html              # Interfața web (single-page)
│
└── static/
    ├── css/style.css           # Stilizare
    └── js/
        ├── i18n.js             # Sistem traduceri RO/EN
        ├── main.js             # Logica UI, apeluri API, randare tabele/grafice
        └── export.js           # Export rezultate PDF
```

**Stack tehnologic:** Python 3, Flask, HTML5/CSS3/JavaScript (vanilla), D3.js, jsPDF

---

## 5. Funcționalități

### 5.1 Selectare Scenariu
Aplicația vine cu **3 scenarii predefinite** selectabile din interfață:

| Scenariu | Agenți | Task-uri | Matrice |
|----------|--------|----------|---------|
| Mic      | 3      | 3        | 3 × 3   |
| Mediu    | 4      | 5        | 4 × 5   |
| Mare     | 6      | 8        | 6 × 8   |

### 5.2 Alocare Aleatorie
Generează 100 de alocări Monte Carlo și afișează costul mediu și deviația standard ca referință.

### 5.3 Alocare Optimă (MODI)
Rezolvă problema prin NV + MODI, returnând costul minim, matricea de alocare și numărul de iterații.

### 5.4 Vizualizare Iterații MODI
Fiecare iterație afișează: tabelul de transport curent, multiplicatorii **u** și **v**, costurile modificate **Δ[i][j]**, circuitul și valoarea **θ**.

### 5.5 Comparare și Economii
Afișează procentul de economie față de media aleatorie și un graf bipartit al fluxurilor (task-uri → agenți).

### 5.6 Interfață Bilingvă (RO / EN)
Buton de limbă fix în colțul dreapta-sus al interfeței — schimbă toate textele UI instant.

### 5.7 Export PDF
Exportă rezultatele complete (matrice, costuri, comparație) ca fișier PDF.

---

## 6. Scenariile Predefinite

### Scenariu Mic (3 × 3)

| Agent | Capacitate | NLP | Computer Vision | Search |
|-------|-----------|-----|-----------------|--------|
| Alpha | 30        | 4   | 6               | 9      |
| Beta  | 25        | 5   | 4               | 7      |
| Omega | 45        | 6   | 3               | 4      |

Volume task-uri: NLP=20, CV=40, Search=40

### Scenariu Mediu (4 × 5)

**Agenți:** Alpha (25), Beta (35), Gamma (40), Delta (30)

**Task-uri:** NLP (20), Computer Vision (30), Recomandări (25), Search (25), Dialog (30)

### Scenariu Mare (6 × 8)

**Agenți:** Alpha (30), Beta (25), Gamma (35), Delta (20), Omega (40), Sigma (30)

**Task-uri:** NLP, Computer Vision, Recomandări, Search, Dialog, Sumarizare, ETL, Monitoring

---

## 7. Algoritmul — Descriere Tehnică

### Faza 1: Metoda Colțului Nord-Vest

Pornind din colțul stânga-sus al matricei, alocă succesiv `min(capacitate[i], volum[j])` și avansează spre dreapta sau în jos. Produce `m + n − 1` celule bazice.

### Faza 2: Metoda Potențialelor / MODI

Iterativ, până la optim:
1. Calculul multiplicatorilor **u, v** din sistemul `u[i] + v[j] = c[i][j]` pe celulele bazice
2. Costurile modificate `Δ[i][j] = c[i][j] − u[i] − v[j]` pentru nebazice
3. Dacă toate `Δ[i][j] ≥ 0` → soluție optimă
4. Altfel: se identifică circuitul BFS, se calculează **θ** și se actualizează baza

### Echilibrare automată

Dacă `Σ capacitate ≠ Σ volum`, se adaugă automat un agent fictiv sau un task fictiv cu cost 0.

---

## 8. API Backend (Flask)

| Endpoint               | Metodă | Descriere                                        |
|------------------------|--------|--------------------------------------------------|
| `/`                    | GET    | Servește interfața web                           |
| `/api/scenarios`       | GET    | Lista scenariilor disponibile                    |
| `/api/scenarios/load`  | POST   | Încarcă un scenariu predefinit sau custom        |
| `/api/cost-matrix`     | POST   | Actualizează matricea de costuri                 |
| `/api/allocate/random` | POST   | 100 alocări aleatoare, returnează statistici     |
| `/api/allocate/optimal`| POST   | Rulează MODI, returnează soluția optimă          |
| `/api/compare`         | POST   | Ambele metode + comparație + graf                |

---

## 9. Rulare

```bash
pip install flask
cd project_fixed
python app.py
```

Deschide browserul la `http://127.0.0.1:5000`.

</details>

---

<details>
<summary><strong>🇬🇧 English</strong></summary>

## 1. Project Purpose

This project simulates a multi-agent system (MAS) in which several specialized AI agents process diverse tasks (NLP, Computer Vision, Search, Dialog, etc.). The central question: **how do you distribute tasks so that the total allocation cost is minimized?**

The answer comes from operations research: the **Transportation Problem**. The implemented library solves this in two phases:

1. **North-West Corner Method** — produces a feasible initial basic solution
2. **MODI / Stepping-Stone Method** — iteratively optimizes until the global optimum is reached

The application visually demonstrates the difference between a **random** task distribution and the **optimized** one, quantifying gains in cost and efficiency.

> Project developed for the **Operations Research** course at the Faculty of Applied Sciences, **Politehnica University of Bucharest (UNSTPB)**.

---

## 2. Objectives

- Minimize total task-allocation cost across AI agents
- Respect each agent's capacity constraint and each task queue's volume requirement
- Exact solution via MODI + North-West Corner
- Visual and numerical comparison against random allocation (100 Monte Carlo runs)

---

## 3. Background & Motivation

A multi-agent system (MAS) is a software architecture in which autonomous agents collaborate to solve complex problems. Each agent has specializations, limited capacity, and a different cost per task type.

Without an intelligent allocation mechanism, arbitrarily distributed tasks lead to agent overload, underutilization, and unjustified costs.

The **Transportation Problem** models exactly this: agents are sources with supply (capacity), tasks are destinations with demand (volume), and the cost of assigning a task to an agent is the processing cost.

---

## 4. Project Architecture

```
project_fixed/
│
├── app.py                      # Flask server (entry point)
├── allocation.py               # Allocation logic: random, MODI, compare, graph
├── agents.py                   # Agent data model
├── tasks.py                    # TaskQueue data model
├── scenarios.py                # 3 predefined scenarios (Small, Medium, Large)
│
├── transport_lib/
│   ├── transport.py            # NW Corner + MODI algorithm implementation
│   
│
├── templates/
│   └── index.html              # Web interface (single-page)
│
└── static/
    ├── css/style.css           # Styling
    └── js/
        ├── i18n.js             # RO/EN translation system
        ├── main.js             # UI logic, API calls, table/graph rendering
        └── export.js           # PDF export
```

**Tech stack:** Python 3, Flask, HTML5/CSS3/JavaScript (vanilla), D3.js, jsPDF

---

## 5. Features

### 5.1 Scenario Selection
Three predefined scenarios selectable from the UI:

| Scenario | Agents | Tasks | Matrix |
|----------|--------|-------|--------|
| Small    | 3      | 3     | 3 × 3  |
| Medium   | 4      | 5     | 4 × 5  |
| Large    | 6      | 8     | 6 × 8  |

### 5.2 Random Allocation
Generates 100 Monte Carlo allocations and displays average cost and standard deviation as a baseline.

### 5.3 Optimal Allocation (MODI)
Solves the problem via NW + MODI, returning the minimum cost, allocation matrix, and iteration count.

### 5.4 MODI Iteration Viewer
Each iteration shows: current transport table, multipliers **u** and **v**, reduced costs **Δ[i][j]**, the identified circuit, and **θ** value.

### 5.5 Comparison & Savings
Displays the savings percentage vs. the random average and a bipartite flow graph (tasks → agents).

### 5.6 Bilingual Interface (RO / EN)
A fixed language button in the top-right corner instantly switches all UI text between Romanian and English.

### 5.7 PDF Export
Exports the full results (matrices, costs, comparison) as a PDF file.

---

## 6. Predefined Scenarios

### Small Scenario (3 × 3)

| Agent | Capacity | NLP | Computer Vision | Search |
|-------|---------|-----|-----------------|--------|
| Alpha | 30      | 4   | 6               | 9      |
| Beta  | 25      | 5   | 4               | 7      |
| Omega | 45      | 6   | 3               | 4      |

Task volumes: NLP=20, CV=40, Search=40

### Medium Scenario (4 × 5)

**Agents:** Alpha (25), Beta (35), Gamma (40), Delta (30)

**Tasks:** NLP (20), Computer Vision (30), Recommendations (25), Search (25), Dialog (30)

### Large Scenario (6 × 8)

**Agents:** Alpha (30), Beta (25), Gamma (35), Delta (20), Omega (40), Sigma (30)

**Tasks:** NLP, Computer Vision, Recommendations, Search, Dialog, Summarization, ETL, Monitoring

---

## 7. Algorithm — Technical Description

### Phase 1: North-West Corner Method

Starting from the top-left of the cost matrix, allocate `min(supply[i], demand[j])` and advance right or down. Produces `m + n − 1` basic cells.

### Phase 2: MODI / Stepping-Stone Method

Iteratively, until optimum:
1. Compute multipliers **u, v** from `u[i] + v[j] = c[i][j]` on basic cells
2. Reduced costs `Δ[i][j] = c[i][j] − u[i] − v[j]` for non-basic cells
3. If all `Δ[i][j] ≥ 0` → optimal solution
4. Otherwise: find the BFS circuit, compute **θ**, update the basis

### Automatic Balancing

If `Σ supply ≠ Σ demand`, a fictitious agent or task with cost 0 is added automatically.

---

## 8. Backend API (Flask)

| Endpoint               | Method | Description                                       |
|------------------------|--------|---------------------------------------------------|
| `/`                    | GET    | Serves the web interface                          |
| `/api/scenarios`       | GET    | List of available scenarios                       |
| `/api/scenarios/load`  | POST   | Load a predefined or custom scenario              |
| `/api/cost-matrix`     | POST   | Update the cost matrix                            |
| `/api/allocate/random` | POST   | 100 random allocations, returns statistics        |
| `/api/allocate/optimal`| POST   | Runs MODI, returns the optimal solution           |
| `/api/compare`         | POST   | Both methods + comparison + graph                 |

---

## 9. Running the App

```bash
pip install flask
cd project_fixed
python app.py
```

Open your browser at `http://127.0.0.1:5000`.

</details>
