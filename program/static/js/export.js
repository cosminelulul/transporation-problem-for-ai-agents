function exportReport(state) {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

  const scenarioName = document.getElementById("scenarioSelect")?.selectedOptions?.[0]?.text || "custom";
  const now = new Date();
  const W = 210, M = 15, contentW = W - M * 2;

  const GREEN_DARK  = [21, 128, 61];
  const GREEN_MID   = [22, 163, 74];
  const GREEN_LIGHT = [220, 252, 231];
  const GREEN_ROW   = [240, 253, 244];
  const GREEN_LABEL = [211, 255, 191];
  const GRAY_BG     = [248, 250, 252];
  const GRAY_TEXT   = [100, 116, 139];
  const WHITE       = [255, 255, 255];
  const TEXT        = [30, 41, 59];
  const YELLOW_HL   = [254, 240, 138];
  const YELLOW_TEXT = [120, 53, 15];
  const RED_LIGHT   = [254, 226, 226];
  const RED_TEXT    = [185, 28, 28];

  let y = 0;
  let pageNum = 1;

  function addPage() {
    doc.addPage();
    pageNum++;
    drawPageFooter();
    y = 20;
  }

  function ensureSpace(needed) {
    if (y + needed > 277) addPage();
  }

  function drawPageFooter() {
    const h = doc.internal.pageSize.height;
    doc.setDrawColor(...GRAY_TEXT);
    doc.setLineWidth(0.3);
    doc.line(M, h - 14, W - M, h - 14);
    doc.setFontSize(8);
    doc.setTextColor(...GRAY_TEXT);
    doc.setFont("helvetica", "normal");
    doc.text(`Pagina ${pageNum}`, W - M, h - 9, { align: "right" });
  }

  // ===== COVER HEADER =====
  doc.setFillColor(...GREEN_DARK);
  doc.rect(0, 0, W, 42, "F");
  doc.setFillColor(...GREEN_MID);
  doc.rect(0, 42, W, 3, "F");

  doc.setTextColor(...WHITE);
  doc.setFontSize(18);
  doc.setFont("helvetica", "bold");
  doc.text("Raport Alocare Multi-Agent", M, 16);
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text(`Scenariu: ${scenarioName}`, M, 25);
  doc.text(`Generat: ${now.toLocaleString("ro-RO")}`, M, 31);

  y = 54;
  drawPageFooter();

  const rand = state.compareResult?.random || state.randomResult;
  const opt  = state.compareResult?.optimal || state.optimalResult;
  const savings = state.compareResult?.savings_pct ?? 0;

  function sectionTitle(num, title) {
    ensureSpace(16);
    doc.setFillColor(...GREEN_DARK);
    doc.rect(M, y, contentW, 9, "F");
    doc.setTextColor(...WHITE);
    doc.setFontSize(11);
    doc.setFont("helvetica", "bold");
    doc.text(`${num}.  ${title}`, M + 4, y + 6.5);
    y += 13;
  }

  // ===== #1 MATRICEA COSTURILOR =====
  sectionTitle("1", "Matricea Costurilor");

  if (state.costMatrix?.length && state.agents?.length && state.tasks?.length) {
    const taskNames = state.tasks.map(t => t.name);
    const taskVols  = state.tasks.map(t => String(t.volume));
    const headCols  = ["Agent", "Capacitate", ...taskNames];
    const volRow    = ["Volum task", "", ...taskVols];
    const bodyRows  = state.agents.map((a, i) => [
      a.name, String(a.capacity),
      ...state.costMatrix[i].map(v => String(v))
    ]);

    doc.autoTable({
      startY: y,
      head: [headCols],
      body: [volRow, ...bodyRows],
      margin: { left: M, right: M },
      styles: { fontSize: 9, cellPadding: 3, valign: "middle", halign: "center" },
      headStyles: { fillColor: GREEN_DARK, textColor: WHITE, fontStyle: "bold", halign: "center" },
      columnStyles: {
        0: { halign: "left", fillColor: GREEN_LABEL, fontStyle: "bold", cellWidth: 32 },
        1: { halign: "center", cellWidth: 22 },
      },
      didParseCell: (data) => {
        if (data.section === "body" && data.row.index === 0) {
          data.cell.styles.fillColor = GREEN_ROW;
          data.cell.styles.textColor = data.column.index === 0 ? GREEN_DARK : GRAY_TEXT;
          if (data.column.index === 0) data.cell.styles.fontStyle = "bold";
        }
        if (data.section === "body" && data.row.index > 0 && (data.row.index - 1) % 2 === 1) {
          if (data.column.index > 1) data.cell.styles.fillColor = GREEN_ROW;
        }
      },
    });
    y = doc.lastAutoTable.finalY + 8;
  } else {
    doc.setFontSize(9); doc.setTextColor(...GRAY_TEXT);
    doc.text("Nu exista date de configurat.", M, y); y += 8;
  }

  // ===== #2 ALOCARE OPTIMA (MODI/Potential) =====
  ensureSpace(20);
  sectionTitle("2", "Alocare Optima (MODI/Potential)");

  if (opt?.allocation?.length) {
    const taskNames = state.tasks.map(t => t.name);
    const headCols  = ["Agent", "Capacitate", ...taskNames, "Total alocat"];
    const bodyRows  = state.agents.map((a, i) => {
      const row   = opt.allocation[i] || [];
      const total = row.reduce((s, v) => s + Number(v), 0);
      return [a.name, String(a.capacity),
        ...row.map(v => Number(v) > 0 ? String(Number(v).toFixed(0)) : "—"),
        String(total.toFixed(0))];
    });

    doc.autoTable({
      startY: y,
      head: [headCols],
      body: bodyRows,
      margin: { left: M, right: M },
      styles: { fontSize: 9, cellPadding: 3, halign: "center" },
      headStyles: { fillColor: GREEN_DARK, textColor: WHITE, fontStyle: "bold" },
      columnStyles: {
        0: { halign: "left", fillColor: GREEN_LABEL, fontStyle: "bold", cellWidth: 32 },
        1: { cellWidth: 22 },
      },
      didParseCell: (data) => {
        if (data.section === "body" && data.column.index > 1) {
          const raw = data.cell.raw;
          if (raw && raw !== "—" && Number(raw) > 0) {
            data.cell.styles.fillColor = [209, 250, 229];
            data.cell.styles.textColor = [5, 150, 105];
            data.cell.styles.fontStyle = "bold";
          }
        }
        if (data.section === "body" && data.row.index % 2 === 1) {
          if (data.column.index < 2) data.cell.styles.fillColor = GREEN_ROW;
        }
      },
    });
    y = doc.lastAutoTable.finalY + 8;
  } else {
    doc.setFontSize(9); doc.setTextColor(...GRAY_TEXT);
    doc.text("Nu exista date de alocare optima.", M, y); y += 8;
  }

  // ===== #3 METRICI =====
  ensureSpace(50);
  sectionTitle("3", "Metrici Comparative");

  if (rand && opt) {
    const metricsData = [
      ["Cost alocare aleatoare (medie 100 rulari)", `${rand.avg_cost}`, "unitati"],
      ["Deviatia standard (aleator)",               `${rand.std_dev}`, "unitati"],
      ["Cost alocare optima (MODI/Potential)",       `${opt.total_cost}`, "unitati"],
      ["Economie realizata",                         `${savings.toFixed(1)}%`, "fata de aleator"],
      ["Numar iteratii MODI/Potential",              `${opt.iterations}`, "pasi"],
      ["Solutie optima confirmata",                  opt.is_optimal ? "DA" : "NU", ""],
    ];

    doc.autoTable({
      startY: y,
      head: [["Metrica", "Valoare", "Unitate"]],
      body: metricsData,
      margin: { left: M, right: M },
      styles: { fontSize: 9, cellPadding: 3 },
      headStyles: { fillColor: GREEN_DARK, textColor: WHITE, fontStyle: "bold" },
      columnStyles: {
        0: { cellWidth: 100 },
        1: { halign: "right", fontStyle: "bold", cellWidth: 30 },
        2: { halign: "left", textColor: GRAY_TEXT, cellWidth: 40 },
      },
      didParseCell: (data) => {
        if (data.section === "body" && data.row.index === 3) {
          data.cell.styles.fillColor = GREEN_LIGHT;
          if (data.column.index === 1) {
            data.cell.styles.textColor = GREEN_DARK;
            data.cell.styles.fontStyle = "bold";
          }
        }
        if (data.section === "body" && data.row.index % 2 === 1) {
          if (!data.cell.styles.fillColor || data.cell.styles.fillColor === WHITE) {
            data.cell.styles.fillColor = GRAY_BG;
          }
        }
      },
    });
    y = doc.lastAutoTable.finalY + 8;
  } else {
    doc.setFontSize(9); doc.setTextColor(...GRAY_TEXT);
    doc.text("Nu exista date comparative. Rulati 'Compara' pentru metrici complete.", M, y); y += 8;
  }

  // ===== #4 TABLOU ITERATIV MODI/POTENTIAL =====
  // Renders the SAME matrix structure visible on the website:
  //   Row 1 header: c_ij | Linie | x_b | [col names with cost values]
  //   Row 2 header: c̃_ij | Baza  | val | [B1 B2 ...]
  //   Body rows:    cb   | xNN   | val | [matrix values, pivot highlighted yellow]
  //   v_j row:      v_j (pot.) |   | [potential values or —]
  //   Δ_ij row:     Δ_ij       |   | [delta values, negative = red]
  // =================================================================

  ensureSpace(20);
  sectionTitle("4", "Tablou Iterativ MODI/Potential");

  // ---- parser: mirrors parseIterationText from main.js ----
  function parseIterText(text) {
    const res = {
      k: 0, pivot: null, cj: [], varNames: [], zj: [], delta: [],
      uValues: [], vValues: [], matrixLines: [], isOptimal: false
    };
    let state = "start";
    const lines = text.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const t = lines[i].trim();
      if (!t) continue;
      const km = t.match(/ITERATIA\s+I_(\d+)/);
      if (km) { res.k = parseInt(km[1]); state = "header"; continue; }
      if (t.match(/^[=\-]{5,}/)) continue;
      const pm = t.match(/Pivot:\s*linie=(\d+)\s*coloana=(\d+)/);
      if (pm) { res.pivot = { row: parseInt(pm[1]) - 1, col: parseInt(pm[2]) - 1 }; continue; }
      if (t.startsWith("u:")) { res.uValues = t.replace(/^u:\s*/,"").split(/\s+/).filter(Boolean); continue; }
      if (t.startsWith("v:")) { res.vValues = t.replace(/^v:\s*/,"").split(/\s+/).filter(Boolean); continue; }
      if (t.startsWith("c_j")) {
        res.cj = t.replace(/c_j\s*->?\s*/,"").trim().split(/\s+/).filter(Boolean);
        state = "body"; continue;
      }
      if (state === "body" && res.cj.length > 0 && res.varNames.length === 0 && t.match(/^(B\d+|x\d+)/)) {
        res.varNames = t.split(/\s+/).filter(Boolean); continue;
      }
      if (t.startsWith("z_j")) { res.zj = t.replace(/z_j\s*->?\s*/,"").trim().split(/\s+/).filter(Boolean); continue; }
      if (t.match(/^[Δ∆D]_j/)) { res.delta = t.replace(/^[Δ∆D]_j\s*->?\s*/,"").trim().split(/\s+/).filter(Boolean); continue; }
      if (state === "body" && t.match(/^-?[\d\/]+\s+\S+\s+/)) {
        const parts = t.replace(/->/g," ").trim().split(/\s+/).filter(Boolean);
        if (parts.length >= 3) res.matrixLines.push(parts);
        continue;
      }
      if (t.includes("OPTIMA") || t.includes("optima")) res.isOptimal = true;
    }
    return res;
  }

  const iterVisuals = opt?.iterations_visual || [];

  if (iterVisuals.length === 0) {
    doc.setFontSize(9); doc.setTextColor(...GRAY_TEXT);
    doc.text("Nu exista date iterative. Rulati 'Alocare optima' mai intai.", M, y); y += 8;
  } else {
    for (let idx = 0; idx < iterVisuals.length; idx++) {
      const parsed   = parseIterText(iterVisuals[idx]);
      const isLast   = idx + 1 === iterVisuals.length;
      const nCols    = parsed.matrixLines.length > 0
        ? parsed.matrixLines[0].length - 3
        : Math.max(parsed.cj.length, parsed.zj.length, parsed.delta.length, 1);
      const cols = parsed.varNames.length > 0
        ? parsed.varNames
        : Array.from({length: nCols}, (_, j) => `B${j+1}`);

      // ---- iteration title bar (green) ----
      ensureSpace(14);
      doc.setFillColor(...GREEN_DARK);
      doc.rect(M, y, contentW, 7, "F");
      doc.setTextColor(...WHITE);
      doc.setFontSize(9);
      doc.setFont("helvetica", "bold");
      const label = `ITERATIA I_${parsed.k}   (${idx + 1} / ${iterVisuals.length})` +
                    (isLast ? "  OPTIM GASIT" : "");
      doc.text(label, M + 3, y + 5);
      y += 9;

      if (parsed.matrixLines.length === 0) {
        doc.setFontSize(8); doc.setTextColor(...GRAY_TEXT);
        doc.text("Date indisponibile pentru aceasta iteratie.", M, y); y += 6;
        continue;
      }

      // ---- build autoTable matching the website layout ----
      // Two header rows: top = c_ij / Linie / x_b / cj values
      //                  sub = c̃_ij / Baza  / val / col names
      // Body rows from matrixLines
      // Then v_j row and Δ_ij row

      const bodyRows = [];
      parsed.matrixLines.forEach((parts, ri) => {
        const cb   = parts[0];
        const base = parts[1];
        const xb   = parts[2];
        const vals = Array.from({length: nCols}, (_, j) =>
          (parts[3 + j] || "0").replace(/->/g, "") || "0"
        );
        bodyRows.push([cb, base, xb, ...vals]);
      });

      // v_j row (zj in parsed)
      bodyRows.push(["vj", "pot.", "", ...Array.from({length: nCols}, (_, j) => parsed.zj[j] || "—")]);
      // Δ_ij row
      bodyRows.push(["Dij", "", "", ...Array.from({length: nCols}, (_, j) => parsed.delta[j] || "·")]);

      const nMatrixRows = parsed.matrixLines.length;
      const vjRowIdx    = nMatrixRows;
      const dijRowIdx   = nMatrixRows + 1;

      const pivR = parsed.pivot?.row;
      const pivC = parsed.pivot?.col;

      ensureSpace(5 + bodyRows.length * 7);

      doc.autoTable({
        startY: y,
        // Two header rows
        head: [
          // Row 1: c_ij | Linie | x_b | cj cost values
          ["c_ij", "Linie", "x_b",
            ...Array.from({length: nCols}, (_, j) => parsed.cj[j] !== undefined ? String(parsed.cj[j]) : "")],
          // Row 2: c̃_ij | Baza | val | column names (B1 B2...)
          ["c_ij", "Baza", "val",
            ...cols.map(c => String(c))],
        ],
        body: bodyRows,
        margin: { left: M, right: M },
        tableWidth: "wrap",
        styles: {
          fontSize: 8, cellPadding: 2.5, halign: "center",
          valign: "middle", overflow: "linebreak",
          font: "helvetica", textColor: TEXT,
        },
        headStyles: {
          fillColor: GREEN_DARK, textColor: WHITE,
          fontStyle: "bold", fontSize: 8, halign: "center",
        },
        didParseCell: (data) => {
          const ri = data.row.index;
          const ci = data.column.index;

          if (data.section === "body") {
            // Label columns (CB, Baza, val)
            if (ci < 3) {
              data.cell.styles.fillColor = GREEN_ROW;
              data.cell.styles.fontStyle = "bold";
              data.cell.styles.halign    = "center";
              data.cell.styles.textColor = GREEN_DARK;
            }

            // v_j row styling
            if (ri === vjRowIdx) {
              data.cell.styles.fillColor = GREEN_ROW;
              data.cell.styles.textColor = GREEN_DARK;
              data.cell.styles.fontStyle = "bold";
              if (ci === 0) {
                // "vj" label → render as v_j (pot.)
                data.cell.text = ["z_ij"];
              }
            }

            // Δ_ij row styling
            if (ri === dijRowIdx) {
              data.cell.styles.fillColor = [240, 253, 244];
              data.cell.styles.fontStyle = "bold";
              if (ci === 0) {
                data.cell.text = ["delta_ij"];
              }
              if (ci >= 3) {
                const val = parseFloat(data.cell.raw);
                if (!isNaN(val) && val < 0) {
                  data.cell.styles.fillColor = RED_LIGHT;
                  data.cell.styles.textColor = RED_TEXT;
                } else if (!isNaN(val)) {
                  data.cell.styles.textColor = GREEN_DARK;
                }
              }
            }

            // Pivot cell highlight (yellow, like on website)
            if (ri < nMatrixRows && ci >= 3) {
              const matCol = ci - 3;
              if (ri === pivR && matCol === pivC) {
                data.cell.styles.fillColor = YELLOW_HL;
                data.cell.styles.textColor = YELLOW_TEXT;
                data.cell.styles.fontStyle = "bold";
              }
            }

            // Zero cells in matrix body → muted
            if (ri < nMatrixRows && ci >= 3) {
              const val = parseFloat(data.cell.raw);
              if (!isNaN(val) && val === 0 && !(ri === pivR && (ci - 3) === pivC)) {
                data.cell.styles.textColor = GRAY_TEXT;
              }
            }

            // Alternating row tint on matrix rows (not vj/dij)
            if (ri < nMatrixRows && ri % 2 === 1 && ci >= 3) {
              if (!data.cell.styles.fillColor || data.cell.styles.fillColor === WHITE) {
                data.cell.styles.fillColor = [245, 253, 248];
              }
            }
          }
        },
      });

      y = doc.lastAutoTable.finalY + 5;

      // Separator between iterations
      if (!isLast) {
        doc.setDrawColor(...GREEN_MID);
        doc.setLineWidth(0.15);
        doc.line(M, y, W - M, y);
        y += 4;
      }
    }

    // Final note
    ensureSpace(14);
    doc.setFontSize(9);
    doc.setFont("helvetica");
    doc.setTextColor(...GREEN_DARK);
    doc.text(
      ` Solutie optima gasita dupa ${iterVisuals.length} iteratii.  Cost total: ${opt.total_cost}`,
      M, y
    );
    y += 8;
  }

  // ===== SAVE =====
  const fname = `raport_alocare_${scenarioName.replace(/\s+/g,"_").toLowerCase()}_${now.toISOString().slice(0,10)}.pdf`;
  doc.save(fname);
}
