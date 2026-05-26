// ============================================================
//  i18n — Traduceri RO / EN
//  Toate textele vizibile din UI sunt aici.
// ============================================================

const TRANSLATIONS = {
  ro: {
    // Header / tabs
    title:           "Optimizator Transport Multi-Agent",
    tab_config:      "Configurare",
    tab_results:     "Rezultate",
    tab_iterations:  "Tablou Iterativ",
    btn_export:      "⬇ Export PDF",

    // Config panel
    h_config:        "Configurare scenariu",
    label_scenario:  "Scenariu",
    btn_load:        "Incarca scenariu",
    btn_add_agent:   "+ Agent",
    btn_add_task:    "+ Task",
    btn_reset:       "Reseteaza matricea",
    btn_apply:       "✓ Aplica configurare",
    h_cost_matrix:   "Matrice costuri",

    // Results panel
    h_results:       "Rulare alocare",
    btn_random:      "Alocare aleatoare",
    btn_optimal:     "Alocare optima",
    btn_compare:     "⚡ Compara",
    h_iterations:    "Tablou Iterativ",

    // Table headers (cost table)
    th_agent:        "Agent",
    th_capacity:     "Capacitate",
    th_tasks:        "Task-uri",
    th_task_volume:  "Volum task",

    // Result cards
    card_random_title:   "Alocare aleatoare",
    card_optimal_title:  "Alocare optima (MODI)",
    lbl_avg_cost:        "Cost mediu:",
    lbl_std_dev:         "Dev. std:",
    lbl_total_cost:      "Cost total:",
    lbl_iterations:      "Iteratii:",
    lbl_optimal:         "Optim:",
    lbl_yes:             "✓ Da",
    lbl_no:              "Nu",
    note_random:         "Alocarea aleatoare distribuie fluxul fara optimizare. Costul mediu arata cum se comporta sistemul in mod probabil, iar variatia indica instabilitate.",
    note_optimal:        "Celulele verzi indica alocari efective. Solutia minimizeaza costul total si respecta toate constrangerile de capacitate si volum.",

    // Metrics
    metric_avg:          "Mediu aleator",
    metric_opt:          "Cost optim",
    metric_savings:      "Economie %",
    metric_iter:         "Iteratii MODI",
    conclusion_prefix:   "Concluzie:",
    conclusion_suffix:   "mai eficient cu alocare optima",
    conclusion_note:     "Comparand costul optim cu media aleatoare, rezultatul arata castigul real al optimizarii.",

    // Iterations panel
    nv_title:         "TABLOU ITERATIV N-V",
    nv_sub:           "Metoda Coltului Nord-Vest — Solutie initiala",
    nv_hint:          "Solutia initiala obtinuta prin Metoda Coltului Nord-Vest. Celulele marcate (galbene) reprezinta alocarile de baza (m+n-1 = {0} celule).",
    nv_agent_task:    "Agent \\ Task",
    nv_offer:         "Ofertă",
    nv_demand:        "Cerere",
    nv_steps_title:   "Pașii metodei Nord-Vest",
    nv_cost_nv:       "Cost soluție NV (inițial)",
    nv_cost_modi:     "Cost optim MODI",
    nv_improvement:   "Imbunatatire MODI",
    nv_no_data:       "Nu exista date de afisat",
    nv_no_data_hint:  "Rulati Alocare optima sau Compara pentru a genera tabloul NV.",

    modi_title:       "TABLOU ITERATIV MODI",
    modi_sub:         "Fiecare iteratie afiseaza tabloul MODI complet. Navigati cu butoanele de mai jos.",
    modi_no_data:     "Nu exista date de afisat",
    modi_no_data_hint:"Rulati Alocare optima sau Compara pentru a genera tabloul iterativ MODI.",
    nav_first:        "⏮ Prima",
    nav_prev:         "◀ Inapoi",
    nav_next:         "Inainte ▶",
    nav_last:         "Ultima ⏭",
    iter_label:       "Iteratia",
    iter_of:          "/",
    iter_found_opt:   "✓ OPTIM GASIT",
    iter_step:        "Pas",
    iter_from:        "din",
    iter_enter:       "→ Intra in baza:",
    iter_exit:        "→ Iese din baza:",
    iter_optimal_msg: "✓ Toate Δj satisfac criteriul de optimalitate. z* = f* =",

    // Table internal labels
    iter_no_matrix:   "Date matrice indisponibile pentru aceasta iteratie",

    // Modal titles
    modal_missing_data:  "Date lipsă",
    modal_no_config:     "Configurare lipsa",
    modal_err_export:    "Eroare - date lipsa",
    modal_err_title:     "Eroare",

    // Modal messages
    msg_no_config:       "Nu au fost incarcate/aplicate date. Incarcati un scenariu si apasati 'Aplica configurare'.",
    msg_no_config_cmp:   "Nu au fost incarcate/aplicate date anterior. Apasati 'Aplica configurare' sau incarcati un scenariu predefinit.",
    msg_no_export:       "Nu au fost incarcate date anterior. Rulati mai intai o alocare sau comparare.",
  },

  en: {
    // Header / tabs
    title:           "Multi-Agent Transport Optimizer",
    tab_config:      "Configuration",
    tab_results:     "Results",
    tab_iterations:  "Iteration Board",
    btn_export:      "⬇ Export PDF",

    // Config panel
    h_config:        "Scenario configuration",
    label_scenario:  "Scenario",
    btn_load:        "Load scenario",
    btn_add_agent:   "+ Agent",
    btn_add_task:    "+ Task",
    btn_reset:       "Reset matrix",
    btn_apply:       "✓ Apply configuration",
    h_cost_matrix:   "Cost matrix",

    // Results panel
    h_results:       "Run allocation",
    btn_random:      "Random allocation",
    btn_optimal:     "Optimal allocation",
    btn_compare:     "⚡ Compare",
    h_iterations:    "Iteration Board",

    // Table headers
    th_agent:        "Agent",
    th_capacity:     "Capacity",
    th_tasks:        "Tasks",
    th_task_volume:  "Task volume",

    // Result cards
    card_random_title:   "Random allocation",
    card_optimal_title:  "Optimal allocation (MODI)",
    lbl_avg_cost:        "Avg. cost:",
    lbl_std_dev:         "Std. dev:",
    lbl_total_cost:      "Total cost:",
    lbl_iterations:      "Iterations:",
    lbl_optimal:         "Optimal:",
    lbl_yes:             "✓ Yes",
    lbl_no:              "No",
    note_random:         "Random allocation distributes flow without optimization. Average cost shows how the system likely behaves, and variance indicates instability.",
    note_optimal:        "Green cells indicate active allocations. The solution minimizes total cost while respecting all capacity and volume constraints.",

    // Metrics
    metric_avg:          "Random average",
    metric_opt:          "Optimal cost",
    metric_savings:      "Savings %",
    metric_iter:         "MODI iterations",
    conclusion_prefix:   "Conclusion:",
    conclusion_suffix:   "more efficient with optimal allocation",
    conclusion_note:     "Comparing optimal cost with the random average shows the real gain from optimization.",

    // Iterations panel
    nv_title:         "N-W ITERATION BOARD",
    nv_sub:           "North-West Corner Method — Initial solution",
    nv_hint:          "Initial solution obtained via the North-West Corner Method. Highlighted cells (yellow) are basic allocations (m+n-1 = {0} cells).",
    nv_agent_task:    "Agent \\ Task",
    nv_offer:         "Supply",
    nv_demand:        "Demand",
    nv_steps_title:   "North-West Corner Steps",
    nv_cost_nv:       "NW solution cost (initial)",
    nv_cost_modi:     "Optimal MODI cost",
    nv_improvement:   "MODI improvement",
    nv_no_data:       "No data to display",
    nv_no_data_hint:  "Run Optimal allocation or Compare to generate the NW board.",

    modi_title:       "MODI ITERATION BOARD",
    modi_sub:         "Each iteration shows the full MODI table. Navigate using the buttons below.",
    modi_no_data:     "No data to display",
    modi_no_data_hint:"Run Optimal allocation or Compare to generate the MODI iteration board.",
    nav_first:        "⏮ First",
    nav_prev:         "◀ Back",
    nav_next:         "Next ▶",
    nav_last:         "Last ⏭",
    iter_label:       "Iteration",
    iter_of:          "/",
    iter_found_opt:   "✓ OPTIMUM FOUND",
    iter_step:        "Step",
    iter_from:        "of",
    iter_enter:       "→ Enters basis:",
    iter_exit:        "→ Leaves basis:",
    iter_optimal_msg: "✓ All Δj satisfy the optimality criterion. z* = f* =",

    // Table internal labels
    iter_no_matrix:   "Matrix data unavailable for this iteration",

    // Modal titles
    modal_missing_data:  "Missing data",
    modal_no_config:     "No configuration",
    modal_err_export:    "Error - no data",
    modal_err_title:     "Error",

    // Modal messages
    msg_no_config:       "No data has been loaded or applied. Load a scenario and press 'Apply configuration'.",
    msg_no_config_cmp:   "No data has been loaded or applied. Press 'Apply configuration' or load a predefined scenario.",
    msg_no_export:       "No data has been loaded. Run an allocation or comparison first.",
  },
};

// ── Starea curentă a limbii ───────────────────────────────────────────────
window.currentLang = "ro";

function t(key, ...args) {
  let text = TRANSLATIONS[window.currentLang][key] || TRANSLATIONS["ro"][key] || key;
  args.forEach((val, idx) => { text = text.replace(`{${idx}}`, val); });
  return text;
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const translation = t(key);
    if (translation) el.textContent = translation;
  });
  document.title = t("title");
  document.documentElement.lang = window.currentLang;
}

function toggleLang() {
  window.currentLang = window.currentLang === "ro" ? "en" : "ro";
  const btn = document.getElementById("langToggle");
  btn.textContent = window.currentLang === "ro" ? "🇬🇧 EN" : "🇷🇴 RO";
  applyTranslations();
  // Re-render UI components that have dynamic text
  if (typeof buildCostTable === "function") buildCostTable();
  if (typeof renderResults === "function") renderResults();
  if (typeof renderIterations === "function") renderIterations();
}
