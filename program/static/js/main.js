const appState = {
  agents: [],
  tasks: [],
  costMatrix: [],
  randomResult: null,
  optimalResult: null,
  compareResult: null,
  configApplied: false,
  currentIterIdx: 0,
  currentNVIterIdx: 0,
};

const els = {
  scenarioSelect:  document.getElementById("scenarioSelect"),
  loadScenarioBtn: document.getElementById("loadScenario"),
  addAgentBtn:     document.getElementById("addAgent"),
  addTaskBtn:      document.getElementById("addTask"),
  resetCostBtn:    document.getElementById("resetCost"),
  saveProblemBtn:  document.getElementById("saveProblem"),
  randomBtn:       document.getElementById("runRandom"),
  optimalBtn:      document.getElementById("runOptimal"),
  compareBtn:      document.getElementById("runCompare"),
  exportBtn:       document.getElementById("exportPdf"),
  costTable:       document.getElementById("costTable"),
  randomBox:       document.getElementById("randomBox"),
  optimalBox:      document.getElementById("optimalBox"),
  metricsBox:      document.getElementById("metricsBox"),
  conclusionBox:   document.getElementById("conclusionBox"),
  iterationsTable: document.getElementById("iterationsTable"),
  tabButtons:      document.querySelectorAll(".tab-btn"),
  tabPanels:       document.querySelectorAll(".tab-panel"),
  toast:           document.getElementById("toast"),
};

const agentNamePool = ["Alpha", "Beta", "Gamma", "Delta", "Omega", "Sigma", "Zeta", "Tau"];
const taskNamePool  = ["NLP", "Computer Vision", "Recomandari", "Search", "Dialog", "Sumarizare", "ETL", "Monitoring"];
const taskTypePool  = ["Decizie"];

// ===== MODAL =====
function showModal(titleKey, messageKey, type = "error") {
  const icons = { error: "⛔", warning: "⚠️", info: "ℹ️" };
  document.getElementById("modalIcon").textContent   = icons[type] || "⚠️";
  document.getElementById("modalTitle").textContent  = typeof titleKey === "string" && titleKey.startsWith("modal_") ? t(titleKey) : titleKey;
  document.getElementById("modalTitle").className    = "modal-title " + type;
  document.getElementById("modalMessage").textContent = typeof messageKey === "string" && messageKey.startsWith("msg_") ? t(messageKey) : messageKey;
  document.getElementById("modalBox").className      = "modal-box " + type;
  document.getElementById("modalClose").className    = "modal-close " + type;
  document.getElementById("modalOverlay").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("modalOverlay").classList.add("hidden");
}

document.getElementById("modalOverlay").addEventListener("click", (e) => {
  if (e.target === document.getElementById("modalOverlay")) closeModal();
});

// ===== API =====
async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function apiPost(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ===== COST TABLE =====
function buildCostTable() {
  const table = els.costTable;
  table.innerHTML = "";

  const thead = document.createElement("thead");

  const topRow = document.createElement("tr");
  const agentHeader = document.createElement("th");
  agentHeader.textContent = t("th_agent");
  agentHeader.rowSpan = 2;
  const capHeader = document.createElement("th");
  capHeader.textContent = t("th_capacity");
  capHeader.rowSpan = 2;
  const taskHeader = document.createElement("th");
  taskHeader.textContent = t("th_tasks");
  taskHeader.colSpan = appState.tasks.length || 1;
  taskHeader.style.textAlign = "center";
  topRow.appendChild(agentHeader);
  topRow.appendChild(capHeader);
  topRow.appendChild(taskHeader);
  thead.appendChild(topRow);

  const nameRow = document.createElement("tr");
  appState.tasks.forEach((task, j) => {
    const th = document.createElement("th");
    const input = document.createElement("input");
    input.type = "text";
    input.value = task.name;
    input.dataset.task = j;
    input.className = "task-name";
    th.appendChild(input);
    nameRow.appendChild(th);
  });
  if (!appState.tasks.length) {
    const th = document.createElement("th");
    th.textContent = t("btn_add_task");
    nameRow.appendChild(th);
  }
  thead.appendChild(nameRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  const volumeRow = document.createElement("tr");
  volumeRow.className = "volume-row";
  const volumeLabel = document.createElement("td");
  volumeLabel.colSpan = 2;
  volumeLabel.textContent = t("th_task_volume");
  volumeRow.appendChild(volumeLabel);
  appState.tasks.forEach((task, j) => {
    const td = document.createElement("td");
    const input = document.createElement("input");
    input.type = "number";
    input.step = "1";
    input.value = task.volume;
    input.dataset.task = j;
    input.className = "task-volume";
    td.appendChild(input);
    volumeRow.appendChild(td);
  });
  if (!appState.tasks.length) {
    const td = document.createElement("td"); td.textContent = "-"; volumeRow.appendChild(td);
  }
  tbody.appendChild(volumeRow);

  appState.agents.forEach((agent, i) => {
    const tr = document.createElement("tr");
    tr.className = "agent-row";

    const nameCell = document.createElement("td");
    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.value = agent.name;
    nameInput.dataset.agent = i;
    nameInput.className = "agent-name";
    nameCell.appendChild(nameInput);

    const capCell = document.createElement("td");
    const capInput = document.createElement("input");
    capInput.type = "number";
    capInput.step = "1";
    capInput.value = agent.capacity;
    capInput.dataset.agent = i;
    capInput.className = "agent-capacity";
    capCell.appendChild(capInput);

    tr.appendChild(nameCell);
    tr.appendChild(capCell);

    appState.tasks.forEach((_, j) => {
      const td = document.createElement("td");
      const input = document.createElement("input");
      input.type = "number";
      input.step = "1";
      input.value = appState.costMatrix[i]?.[j] ?? 0;
      input.dataset.row = i;
      input.dataset.col = j;
      td.appendChild(input);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  if (appState.tasks.length > 5) {
    table.classList.add("compact");
  } else {
    table.classList.remove("compact");
  }
}

function collectProblemFromCostTable() {
  const taskNameInputs   = els.costTable.querySelectorAll(".task-name");
  const taskVolumeInputs = els.costTable.querySelectorAll(".task-volume");
  const tasks = Array.from(taskNameInputs).map((input, idx) => ({
    id: `T${idx + 1}`,
    name: input.value || taskNamePool[idx % taskNamePool.length],
    volume: Number(taskVolumeInputs[idx]?.value || 0),
    type: taskTypePool[0],
  }));

  const agentRows = els.costTable.querySelectorAll(".agent-row");
  const agents = Array.from(agentRows).map((row, idx) => {
    const name     = row.querySelector(".agent-name").value     || agentNamePool[idx % agentNamePool.length];
    const capacity = Number(row.querySelector(".agent-capacity").value || 0);
    return { id: `A${idx + 1}`, name, capacity };
  });

  const matrix = [];
  agents.forEach((_, i) => {
    const row = [];
    tasks.forEach((__, j) => {
      const input = els.costTable.querySelector(`input[data-row="${i}"][data-col="${j}"]`);
      row.push(Number(input?.value || 0));
    });
    matrix.push(row);
  });

  return { agents, tasks, costMatrix: matrix };
}

// ===== RENDER RESULTS =====
function renderMatrixTable(matrix, rowLabels, colLabels, highlightPositive = false) {
  if (!matrix?.length) return "";
  const headerCells = colLabels.map(tl => `<th>${tl}</th>`).join("");
  const header = `<thead><tr><th></th>${headerCells}</tr></thead>`;
  const body = matrix.map((row, i) => {
    const cells = row.map((v) => {
      const val = Number(v).toFixed(2);
      const isActive = highlightPositive && Number(v) > 0;
      return `<td class="${isActive ? "active-cell" : ""}">${val}</td>`;
    }).join("");
    return `<tr><td>${rowLabels[i] || `Agent ${i + 1}`}</td>${cells}</tr>`;
  }).join("");
  return `<table class="matrix-table">${header}<tbody>${body}</tbody></table>`;
}

function renderResults() {
  const rand    = appState.compareResult?.random  || appState.randomResult;
  const opt     = appState.compareResult?.optimal || appState.optimalResult;
  const savings = appState.compareResult?.savings_pct;

  const agentNames = appState.agents.map(a => a.name);
  const taskNames  = appState.tasks.map(tk => tk.name);

  if (rand) {
    els.randomBox.innerHTML = `
      <h3>${t("card_random_title")}</h3>
      <p><strong>${t("lbl_avg_cost")}</strong> ${rand.avg_cost} &nbsp; <strong>${t("lbl_std_dev")}</strong> ${rand.std_dev}</p>
      ${renderMatrixTable(rand.sample_allocation, agentNames, taskNames, false)}
      <p class="result-note">${t("note_random")}</p>
    `;
  }

  if (opt) {
    els.optimalBox.innerHTML = `
      <h3>${t("card_optimal_title")}</h3>
      <p><strong>${t("lbl_total_cost")}</strong> ${opt.total_cost} &nbsp; <strong>${t("lbl_iterations")}</strong> ${opt.iterations} &nbsp; <strong>${t("lbl_optimal")}</strong> ${opt.is_optimal ? t("lbl_yes") : t("lbl_no")}</p>
      ${renderMatrixTable(opt.allocation, agentNames, taskNames, true)}
      <p class="result-note">${t("note_optimal")}</p>
    `;
  }

  if (rand && opt) {
    els.metricsBox.innerHTML = `
      <div class="metric"><span class="label">${t("metric_avg")}</span><span class="value">${rand.avg_cost}</span></div>
      <div class="metric"><span class="label">${t("metric_opt")}</span><span class="value">${opt.total_cost}</span></div>
      <div class="metric"><span class="label">${t("metric_savings")}</span><span class="value">${savings ?? 0}%</span></div>
      <div class="metric"><span class="label">${t("metric_iter")}</span><span class="value">${opt.iterations}</span></div>
    `;
    const efficiency = savings ? `${savings}%` : "0%";
    els.conclusionBox.innerHTML = `${t("conclusion_prefix")} <strong>${efficiency}</strong> ${t("conclusion_suffix")} <small>${t("conclusion_note")}</small>`;
  } else {
    els.conclusionBox.innerHTML = "";
  }

  renderIterations();
}

// ===== PARSE CLI ITERATION TEXT → STRUCTURED TABLE =====
function parseIterationText(text) {
  const lines = text.split("\n");
  const result = { k: 0, pivot: null, cj: [], varNames: [], zj: [], delta: [], enterVar: null, exitVar: null, matrixLines: [] };

  let state = "start";

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();

    const kMatch = trimmed.match(/ITERATIA\s+I_(\d+)/);
    if (kMatch) { result.k = parseInt(kMatch[1]); state = "header"; continue; }

    if (trimmed.match(/^[-=]{5,}/)) { continue; }

    const pivotMatch = trimmed.match(/Pivot:.*?linie=(\d+).*?coloana=(\d+)/);
    if (pivotMatch) { result.pivot = { row: parseInt(pivotMatch[1]) - 1, col: parseInt(pivotMatch[2]) - 1 }; continue; }

    if (trimmed.startsWith("c_j")) {
      result.cj = trimmed.replace(/c_j\s*->?\s*/, "").trim().split(/\s+/).filter(Boolean);
      continue;
    }

    if (result.cj.length > 0 && result.varNames.length === 0 && trimmed.match(/^(x\d+|a\d+|y\d+|z\d+|B\d+)/)) {
      result.varNames = trimmed.split(/\s+/).filter(Boolean);
      state = "body";
      continue;
    }

    if (trimmed.startsWith("z_j")) {
      result.zj = trimmed.replace(/z_j\s*->?\s*/, "").trim().split(/\s+/).filter(Boolean);
      continue;
    }

    if (trimmed.startsWith("Δ_j") || trimmed.startsWith("D_j") || trimmed.startsWith("\u0394_j")) {
      result.delta = trimmed.replace(/^[\u0394D]_j\s*->?\s*/, "").trim().split(/\s+/).filter(Boolean);
      continue;
    }

    if (state === "body" && !trimmed.startsWith("z_j") && !trimmed.startsWith("Δ") && !trimmed.startsWith("->")) {
      const parts = trimmed.replace(/->/g, " ").trim().split(/\s+/).filter(Boolean);
      if (parts.length >= 4) { result.matrixLines.push(parts); }
      continue;
    }

    const enterMatch = trimmed.match(/Intra in baza:\s*(\S+)/);
    if (enterMatch) result.enterVar = enterMatch[1];
    const exitMatch  = trimmed.match(/Iese din baza:\s*(\S+)/);
    if (exitMatch)  result.exitVar  = exitMatch[1];
  }

  return result;
}

function renderIterationAsTable(parsed) {
  const { k, pivot, cj, varNames, matrixLines, zj, delta, enterVar, exitVar } = parsed;

  const cols   = varNames.length > 0 ? varNames : [];
  const nCols  = Math.max(cols.length, cj.length, zj.length, delta.length,
    matrixLines.length > 0 ? matrixLines[0].length - 3 : 0);
  const isCompact = nCols > 10;

  let html = `<div class="simplex-table-wrap">`;
  html += `<table class="simplex-table${isCompact ? " compact" : ""}">`;
  html += `<thead>`;

  html += `<tr class="cj-row"><th class="row-label">c<sub>j</sub> →</th><th class="row-label">Baza</th><th class="row-label">x<sub>b</sub></th>`;
  for (let j = 0; j < nCols; j++) html += `<th>${cj[j] !== undefined ? cj[j] : ""}</th>`;
  html += `</tr>`;

  html += `<tr><th class="row-label">C<sub>B</sub></th><th class="row-label">Baza</th><th class="row-label">x<sub>b</sub></th>`;
  for (let j = 0; j < nCols; j++) html += `<th>${cols[j] || `x${j+1}`}</th>`;
  html += `</tr></thead><tbody>`;

  if (matrixLines.length === 0) {
    html += `<tr><td colspan="${nCols + 3}" style="text-align:center; color:var(--muted); padding:12px;">${t("iter_no_matrix")}</td></tr>`;
  } else {
    matrixLines.forEach((parts, i) => {
      const cb   = parts[0];
      const base = parts[1];
      const xb   = parts[2];
      html += `<tr>`;
      html += `<td class="row-label">${cb}</td>`;
      html += `<td class="row-label">${base}</td>`;
      html += `<td>${xb}</td>`;
      for (let j = 0; j < nCols; j++) {
        const rawVal  = parts[3 + j] !== undefined ? parts[3 + j].replace(/->/, "") : "0";
        const isPivot = pivot && pivot.row === i && pivot.col === j;
        html += `<td class="${isPivot ? "pivot-cell" : ""}">${rawVal || "0"}</td>`;
      }
      html += `</tr>`;
    });
  }

  html += `<tr class="zj-row"><td class="row-label" colspan="2">z<sub>j</sub></td><td></td>`;
  for (let j = 0; j < nCols; j++) html += `<td>${zj[j] || "0"}</td>`;
  html += `</tr>`;

  html += `<tr class="delta-row"><td class="row-label" colspan="2">Δ<sub>j</sub></td><td></td>`;
  for (let j = 0; j < nCols; j++) {
    const val   = delta[j] || "0";
    const isNeg = parseFloat(val) < 0;
    html += `<td class="${isNeg ? "negative" : ""}">${val}</td>`;
  }
  html += `</tr>`;

  html += `</tbody></table></div>`;
  return html;
}

// ===== NV TABLEAU =====
function buildNVTableau() {
  const opt = appState.compareResult?.optimal || appState.optimalResult;
  if (!opt) return null;

  const agents = appState.agents;
  const tasks  = appState.tasks;
  const supply = agents.map(a => a.capacity);
  const demand = tasks.map(tk => tk.volume);
  const m = agents.length;
  const n = tasks.length;

  const remSupply = [...supply];
  const remDemand = [...demand];
  const alloc     = Array.from({length: m}, () => new Array(n).fill(0));
  const steps     = [];

  let i = 0, j = 0;
  while (i < m && j < n) {
    const val = Math.min(remSupply[i], remDemand[j]);
    alloc[i][j] = val;
    steps.push({ i, j, val, supplyBefore: remSupply[i], demandBefore: remDemand[j] });
    remSupply[i] -= val;
    remDemand[j] -= val;
    if (remSupply[i] === 0 && remDemand[j] === 0) {
      if (i + 1 < m && j + 1 < n) { i++; j++; }
      else if (i + 1 < m) i++;
      else j++;
    } else if (remSupply[i] === 0) i++;
    else j++;
  }

  const costMatrix = appState.costMatrix;
  let nvCost = 0;
  for (let ri = 0; ri < m; ri++)
    for (let rj = 0; rj < n; rj++)
      nvCost += alloc[ri][rj] * (costMatrix[ri]?.[rj] || 0);

  return { alloc, steps, nvCost: Math.round(nvCost * 100) / 100, m, n };
}

function renderNVTableau() {
  const nvData = buildNVTableau();
  if (!nvData) {
    return `<div style="text-align:center; padding:40px; color:var(--muted);">
      <div style="font-size:48px; margin-bottom:12px;">📊</div>
      <div style="font-size:16px; font-weight:600; color:#1e293b; margin-bottom:8px;">${t("nv_no_data")}</div>
      <div style="font-size:13px;">${t("nv_no_data_hint")}</div>
    </div>`;
  }

  const { alloc, steps, nvCost, m, n } = nvData;
  const agents     = appState.agents;
  const tasks      = appState.tasks;
  const costMatrix = appState.costMatrix;

  let html = `<div class="nv-section">`;
  html += `<p class="hint">${t("nv_hint", m + n - 1)}</p>`;

  html += `<div class="simplex-table-wrap"><table class="simplex-table nv-table">`;
  html += `<thead><tr><th class="row-label">${t("nv_agent_task")}</th>`;
  tasks.forEach(tk => { html += `<th>${tk.name}</th>`; });
  html += `<th class="supply-col">${t("nv_offer")}</th></tr></thead><tbody>`;

  for (let i = 0; i < m; i++) {
    html += `<tr>`;
    html += `<td class="row-label">${agents[i].name}</td>`;
    for (let j = 0; j < n; j++) {
      const isBasic = alloc[i][j] > 0;
      const cost    = costMatrix[i]?.[j] || 0;
      html += `<td class="${isBasic ? "nv-basic-cell" : ""}">`;
      if (isBasic) {
        html += `<span class="nv-alloc">${alloc[i][j]}</span><span class="nv-cost">c=${cost}</span>`;
      } else {
        html += `<span class="nv-cost-only">c=${cost}</span>`;
      }
      html += `</td>`;
    }
    html += `<td class="supply-col">${agents[i].capacity}</td>`;
    html += `</tr>`;
  }

  html += `<tr class="demand-row"><td class="row-label">${t("nv_demand")}</td>`;
  tasks.forEach(tk => { html += `<td>${tk.volume}</td>`; });
  html += `<td class="supply-col" style="color:var(--accent-2);font-weight:700;">—</td></tr>`;
  html += `</tbody></table></div>`;

  html += `<div class="nv-steps">`;
  html += `<div class="nv-steps-title">${t("nv_steps_title")}</div>`;
  html += `<div class="nv-steps-list">`;
  steps.forEach((s, idx) => {
    html += `<div class="nv-step">
      <span class="nv-step-num">${idx + 1}</span>
      <span class="nv-step-text">
        x<sub>${s.i+1},${s.j+1}</sub> = min(${s.supplyBefore}, ${s.demandBefore}) = <strong>${s.val}</strong>
        → <em>${agents[s.i].name}</em> ← <em>${tasks[s.j].name}</em>
      </span>
    </div>`;
  });
  html += `</div></div>`;

  const opt        = appState.compareResult?.optimal || appState.optimalResult;
  const optCost    = opt?.total_cost;
  const improvement = optCost !== undefined ? Math.round(((nvCost - optCost) / nvCost) * 1000) / 10 : null;

  html += `<div class="nv-cost-summary">`;
  html += `<div class="nv-cost-item"><span class="label">${t("nv_cost_nv")}</span><span class="value nv-cost-val">${nvCost}</span></div>`;
  if (optCost !== undefined) {
    html += `<div class="nv-cost-item"><span class="label">${t("nv_cost_modi")}</span><span class="value opt-cost-val">${optCost}</span></div>`;
    if (improvement > 0) {
      html += `<div class="nv-cost-item"><span class="label">${t("nv_improvement")}</span><span class="value imp-val">${improvement}%</span></div>`;
    }
  }
  html += `</div>`;
  html += `</div>`;
  return html;
}

function renderIterations() {
  const opt       = appState.compareResult?.optimal || appState.optimalResult;
  const container = els.iterationsTable;
  container.innerHTML = "";

  // ===== NV SECTION =====
  const nvSection = document.createElement("div");
  nvSection.className = "iter-section";
  nvSection.innerHTML = `
    <div class="iter-section-header">
      <span class="iter-section-title">${t("nv_title")}</span>
      <span class="iter-section-sub">${t("nv_sub")}</span>
    </div>
    <div class="iter-section-body">
      ${renderNVTableau()}
    </div>
  `;
  container.appendChild(nvSection);

  // ===== MODI SECTION =====
  const simplexSection = document.createElement("div");
  simplexSection.className = "iter-section";

  if (!opt?.iterations_visual?.length) {
    simplexSection.innerHTML = `
      <div class="iter-section-header">
        <span class="iter-section-title">${t("modi_title")}</span>
        <span class="iter-section-sub">${t("modi_sub")}</span>
      </div>
      <div style="text-align:center; padding:40px; color:var(--muted);">
        <div style="font-size:48px; margin-bottom:12px;">📊</div>
        <div style="font-size:16px; font-weight:600; color:#1e293b; margin-bottom:8px;">${t("modi_no_data")}</div>
        <div style="font-size:13px;">${t("modi_no_data_hint")}</div>
      </div>`;
    container.appendChild(simplexSection);
    return;
  }

  const visuals = opt.iterations_visual;
  const total   = visuals.length;
  appState.currentIterIdx = 0;

  simplexSection.innerHTML = `
    <div class="iter-section-header">
      <span class="iter-section-title">${t("modi_title")}</span>
      <span class="iter-section-sub">${t("modi_sub")}</span>
    </div>
    <div class="iter-section-body" id="simplexIterBody"></div>
  `;
  container.appendChild(simplexSection);

  function renderSimplexCurrent() {
    const idx    = appState.currentIterIdx;
    const text   = visuals[idx];
    const parsed = parseIterationText(text);
    const isLast = idx + 1 === total;

    let cardHtml = `
      <div class="iteration-nav">
        <button class="nav-btn" id="iterFirst" onclick="iterNav('first')">${t("nav_first")}</button>
        <button class="nav-btn" id="iterPrev"  onclick="iterNav('prev')">${t("nav_prev")}</button>
        <span class="iter-counter">${t("iter_label")} ${idx + 1} ${t("iter_of")} ${total}</span>
        <button class="nav-btn" id="iterNext"  onclick="iterNav('next')">${t("nav_next")}</button>
        <button class="nav-btn" id="iterLast"  onclick="iterNav('last')">${t("nav_last")}</button>
      </div>
      <div class="iteration-display">
        <div class="iteration-card">
          <div class="iteration-header">
            <span class="iter-title">ITERATIA I_${parsed.k}</span>
            <span>${isLast ? t("iter_found_opt") : `${t("iter_step")} ${idx + 1} ${t("iter_from")} ${total}`}</span>
          </div>
          <div class="iteration-body">
            ${renderIterationAsTable(parsed)}
    `;

    if (parsed.enterVar || parsed.exitVar) {
      cardHtml += `<div class="iter-pivot-info">`;
      if (parsed.enterVar) cardHtml += `${t("iter_enter")} <strong>${parsed.enterVar}</strong> &nbsp;`;
      if (parsed.exitVar)  cardHtml += `${t("iter_exit")} <strong>${parsed.exitVar}</strong>`;
      cardHtml += `</div>`;
    }

    if (isLast) {
      cardHtml += `<div class="iter-optimal-info">${t("iter_optimal_msg")} ${opt.total_cost}</div>`;
    }

    cardHtml += `</div></div></div>`;

    document.getElementById("simplexIterBody").innerHTML = cardHtml;
    document.getElementById("iterFirst").disabled = idx === 0;
    document.getElementById("iterPrev").disabled  = idx === 0;
    document.getElementById("iterNext").disabled  = idx === total - 1;
    document.getElementById("iterLast").disabled  = idx === total - 1;
  }

  window.iterNav = function(dir) {
    const tot = (appState.compareResult?.optimal || appState.optimalResult)?.iterations_visual?.length || 0;
    if (dir === "first") appState.currentIterIdx = 0;
    else if (dir === "prev")  appState.currentIterIdx = Math.max(0, appState.currentIterIdx - 1);
    else if (dir === "next")  appState.currentIterIdx = Math.min(tot - 1, appState.currentIterIdx + 1);
    else if (dir === "last")  appState.currentIterIdx = tot - 1;
    renderSimplexCurrent();
  };

  renderSimplexCurrent();
}

// ===== SCENARIOS =====
async function loadScenarios() {
  const scenarios = await apiGet("/api/scenarios");
  scenarios.forEach((sc) => {
    const opt = document.createElement("option");
    opt.value       = sc.id;
    opt.textContent = sc.name;
    els.scenarioSelect.appendChild(opt);
  });
}

async function loadScenarioById(id) {
  const data = await apiPost("/api/scenarios/load", { scenario_id: id });
  appState.agents        = data.agents;
  appState.tasks         = data.tasks;
  appState.costMatrix    = data.cost_matrix;
  appState.configApplied = false;
  buildCostTable();
}

async function saveCurrentProblem() {
  const { agents, tasks, costMatrix } = collectProblemFromCostTable();
  const data = await apiPost("/api/scenarios/load", {
    scenario_id: "custom",
    agents,
    tasks,
    cost_matrix: costMatrix,
  });
  appState.agents        = data.agents;
  appState.tasks         = data.tasks;
  appState.costMatrix    = data.cost_matrix;
  appState.configApplied = true;
  buildCostTable();
}

async function runRandom() {
  if (!appState.configApplied) {
    showModal("modal_missing_data", "msg_no_config", "error"); return;
  }
  await saveCurrentProblem();
  appState.randomResult  = await apiPost("/api/allocate/random", {});
  appState.compareResult = null;
  renderResults();
}

async function runOptimal() {
  if (!appState.configApplied) {
    showModal("modal_missing_data", "msg_no_config", "error"); return;
  }
  await saveCurrentProblem();
  appState.optimalResult = await apiPost("/api/allocate/optimal", {});
  appState.compareResult = null;
  renderResults();
}

async function runCompare() {
  if (!appState.configApplied) {
    showModal("modal_no_config", "msg_no_config_cmp", "error"); return;
  }
  await saveCurrentProblem();
  appState.compareResult = await apiPost("/api/compare", {});
  appState.randomResult  = null;
  appState.optimalResult = null;
  renderResults();
}

// ===== EVENTS =====
els.loadScenarioBtn.addEventListener("click", async () => {
  await loadScenarioById(els.scenarioSelect.value);
});

els.addAgentBtn.addEventListener("click", () => {
  appState.agents.push({ id: `A${appState.agents.length + 1}`, name: agentNamePool[appState.agents.length % agentNamePool.length], capacity: 10 });
  appState.costMatrix.push(new Array(appState.tasks.length).fill(0));
  appState.configApplied = false;
  buildCostTable();
});

els.addTaskBtn.addEventListener("click", () => {
  appState.tasks.push({ id: `T${appState.tasks.length + 1}`, name: taskNamePool[appState.tasks.length % taskNamePool.length], volume: 10, type: taskTypePool[0] });
  appState.costMatrix.forEach((row) => row.push(0));
  appState.configApplied = false;
  buildCostTable();
});

els.resetCostBtn.addEventListener("click", () => {
  appState.costMatrix    = appState.agents.map(() => new Array(appState.tasks.length).fill(0));
  appState.configApplied = false;
  buildCostTable();
});

els.costTable.addEventListener("input",  () => { appState.configApplied = false; });
els.saveProblemBtn.addEventListener("click", saveCurrentProblem);
els.randomBtn.addEventListener("click",  runRandom);
els.optimalBtn.addEventListener("click", runOptimal);
els.compareBtn.addEventListener("click", runCompare);

els.exportBtn.addEventListener("click", () => {
  const rand = appState.compareResult?.random  || appState.randomResult;
  const opt  = appState.compareResult?.optimal || appState.optimalResult;
  if (!rand && !opt) {
    showModal("modal_err_export", "msg_no_export", "error"); return;
  }
  exportReport(appState);
});

els.tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    els.tabButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const target = btn.dataset.tab;
    els.tabPanels.forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.tabPanel === target);
    });
  });
});

async function init() {
  await loadScenarios();
  await loadScenarioById("small");
}

init();

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.remove("hidden");
  setTimeout(() => { els.toast.classList.add("hidden"); }, 5000);
}
