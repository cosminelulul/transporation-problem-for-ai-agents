import copy
from fractions import Fraction

# ============================================================
#  Constante aparenta
# ============================================================
A_Settings = {
    "BG_DARK"        : "#1A1A1B",
    "BG_PANEL"       : "#111112",
    "BG_CARD"        : "#252527",
    "BG_INPUT"       : "#2E2E30",
    "BG_HEADER"      : "#1F1F21",
    "ACCENT"         : "#7B68EE",
    "ACCENT2"        : "#45454E",
    "GREEN"          : "#3ecf8e",
    "RED"            : "#f75f5f",
    "YELLOW"         : "#f7c948",
    "TEXT_MAIN"      : "#F6E8E8",
    "TEXT_DIM"       : "#D1DCDF",
    "TEXT_HEAD"      : "#F4CDCD",
    "MONO_FONT"      : ("Consolas", 12),
    "MONO_BIG"       : ("Consolas", 13),
    "TITLE_FONT"     : ("Segoe UI", 15, "bold"),
    "LABEL_FONT"     : ("Segoe UI", 14),
    "BTN_FONT"       : ("Segoe UI", 12, "bold"),
    "GRID_HDR_FONT"  : ("Segoe UI", 13, "bold"),
    "GRID_LABEL_FONT": ("Segoe UI", 13, "bold"),
    "GRID_ENTRY_FONT": ("Consolas", 13),
    "SPINBOX_FONT"   : ("Segoe UI", 14),
}

# ============================================================
#  Utilitare Fraction
# ============================================================
def F(x):
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(x).limit_denominator(10**9)
    except Exception:
        return Fraction(0)

def fmt(v):
    v = F(v)
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


# ============================================================
#  PAS 1 – Echilibrare
# ============================================================
def echilibreaza(a, b, c):
    """
    Returneaza (a', b', c') echilibrate (sum a' == sum b'),
    plus fictiva_sursa (bool) si fictiva_dest (bool).
    """
    a = [F(x) for x in a]
    b = [F(x) for x in b]
    c = [list(map(F, row)) for row in c]

    Sa = sum(a)
    Sb = sum(b)

    fictiva_sursa = False
    fictiva_dest  = False

    if Sa > Sb:
        # adaugam destinatie fictiva Bn+1
        diff = Sa - Sb
        b.append(diff)
        for i in range(len(a)):
            c[i].append(F(0))
        fictiva_dest = True
    elif Sb > Sa:
        # adaugam sursa fictiva Am+1
        diff = Sb - Sa
        a.append(diff)
        c.append([F(0)] * len(b))
        fictiva_sursa = True

    return a, b, c, fictiva_sursa, fictiva_dest


# ============================================================
#  PAS 2 – Metoda Coltului N-V  (solutie de baza initiala)
# ============================================================
def metoda_NV(a, b):
    """
    Returneaza x (matrice m x n) si multimea celulelor bazice J.
    a, b sunt copii mutabile (le vom modifica).
    """
    m = len(a)
    n = len(b)
    a = list(a)
    b = list(b)
    x = [[F(0)] * n for _ in range(m)]
    J = []   # celule bazice (i, j)

    i, j = 0, 0
    while i < m and j < n:
        val = min(a[i], b[j])
        x[i][j] = val
        J.append((i, j))
        a[i] -= val
        b[j] -= val
        if a[i] == 0 and b[j] == 0:
            # degenerare potentiala: avansam pe diagonala
            if i + 1 < m and j + 1 < n:
                i += 1
                j += 1
            elif i + 1 < m:
                i += 1
            else:
                j += 1
        elif a[i] == 0:
            i += 1
        else:
            j += 1

    return x, J


# ============================================================
#  PAS 3 – Costul total al solutiei curente
# ============================================================
def cost_total(x, c, J):
    return sum(c[i][j] * x[i][j] for (i, j) in J)


# ============================================================
#  PAS 4 – Calculul multiplicatorilor u, v  (sistemul S)
# ============================================================
def calculeaza_uv(c, J, m, n):
    """
    Rezolva sistemul  u[i] + v[j] = c[i][j]  pentru (i,j) in J.
    Conventia: u[0] = 0.
    """
    u = [None] * m
    v = [None] * n
    u[0] = F(0)

    changed = True
    while changed:
        changed = False
        for (i, j) in J:
            if u[i] is not None and v[j] is None:
                v[j] = c[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = c[i][j] - v[j]
                changed = True

    # daca mai sunt None, le punem 0 (nu ar trebui pentru PTE nedegenerat)
    u = [x if x is not None else F(0) for x in u]
    v = [x if x is not None else F(0) for x in v]
    return u, v


# ============================================================
#  PAS 5 – Costurile modificate delta[i][j]
# ============================================================
def calculeaza_delta(c, u, v, J, m, n):
    J_set = set(J)
    delta = {}
    for i in range(m):
        for j in range(n):
            if (i, j) not in J_set:
                delta[(i, j)] = c[i][j] - u[i] - v[j]
    return delta


# ============================================================
#  PAS 7 – Circuitul (ciclul) pentru celula (p, q)
# ============================================================
def gaseste_circuit(p, q, J):
    """
    Construieste ciclul care porneste din (p,q), trece prin celule
    din J si revine in (p,q). Returneaza lista ordonata de celule
    (inclusiv (p,q) la inceput), sau None daca nu exista.
    """
    J_set = set(J) | {(p, q)}

    def dfs(path, last_dir):
        ci, cj = path[-1]
        if len(path) >= 4 and (ci, cj) == (p, q):
            return path[:]
        # alternam directia: 'row' sau 'col'
        if last_dir == 'row':
            # miscam pe coloana: acelasi j, alta linie
            for ni in range(len(set(r for r, _ in J_set))):
                pass
            candidates = [(ni, cj) for (ni, nj) in J_set if nj == cj and ni != ci]
        else:
            candidates = [(ci, nj) for (ni, nj) in J_set if ni == ci and nj != cj]

        for cell in candidates:
            if cell == (p, q) and len(path) >= 3:
                return path + [(p, q)]
            if cell not in path:
                res = dfs(path + [cell], 'row' if last_dir == 'col' else 'col')
                if res is not None:
                    return res
        return None

    # incercam ambele directii de pornire
    result = dfs([(p, q)], 'col')
    if result is None:
        result = dfs([(p, q)], 'row')
    return result


def gaseste_circuit_v2(p, q, J):
    """
    Varianta iterativa (BFS pe graful bipartit linie-coloana).
    Returneaza lista de celule ale ciclului (fara duplicarea startului),
    sau None.
    """
    # celule disponibile (bazice + (p,q))
    celule = set(J) | {(p, q)}

    # construim graful linie->coloane si coloana->linii
    from collections import defaultdict
    row2cols = defaultdict(set)
    col2rows = defaultdict(set)
    for (i, j) in celule:
        row2cols[i].add(j)
        col2rows[j].add(i)

    # BFS: starile sunt (celula_curenta, directie_urmatoare)
    # directia indica daca urmatorul pas e pe linie sau pe coloana
    from collections import deque
    # (cale, dir_urmator)  dir: 'r'=miscare pe linie(acelasi i), 'c'=miscare pe coloana
    # pornim din (p,q); primul pas poate fi pe linie SAU pe coloana
    for start_dir in ('r', 'c'):
        queue = deque()
        queue.append(([(p, q)], start_dir))
        visited_states = set()
        visited_states.add(((p, q), start_dir))

        while queue:
            path, nxt_dir = queue.popleft()
            ci, cj = path[-1]

            if nxt_dir == 'r':
                # miscam pe aceeasi linie (acelasi i, alt j)
                for nj in row2cols[ci]:
                    if nj == cj:
                        continue
                    nc = (ci, nj)
                    if nc == (p, q) and len(path) >= 3:
                        return path + [(p, q)]
                    if nc not in path:
                        state = (nc, 'c')
                        if state not in visited_states:
                            visited_states.add(state)
                            queue.append((path + [nc], 'c'))
            else:
                # miscam pe aceeasi coloana (acelasi j, alt i)
                for ni in col2rows[cj]:
                    if ni == ci:
                        continue
                    nc = (ni, cj)
                    if nc == (p, q) and len(path) >= 3:
                        return path + [(p, q)]
                    if nc not in path:
                        state = (nc, 'r')
                        if state not in visited_states:
                            visited_states.add(state)
                            queue.append((path + [nc], 'r'))
    return None


# ============================================================
#  Algoritm principal: rezolva_transport
# ============================================================
def rezolva_transport(a_in, b_in, c_in):
    """
    Returneaza un dict cu:
      status       : 'optimal' | 'error'
      iterations   : lista de snapshot-uri
      x_opt        : matricea optima (m_orig x n_orig)
      f_opt        : valoarea optima
      fictiva_sursa, fictiva_dest : bool
      m_orig, n_orig, m, n
    """
    m_orig = len(a_in)
    n_orig = len(c_in[0]) if c_in else 0

    # PAS 1 – Echilibrare
    a, b, c, fictiva_sursa, fictiva_dest = echilibreaza(a_in, b_in, c_in)
    m = len(a)
    n = len(b)

    Sa = sum(a)
    Sb = sum(b)

    # PAS 2 – Solutie initiala NV
    x = [[F(0)] * n for _ in range(m)]
    a_copy = list(a)
    b_copy = list(b)
    x0, J = metoda_NV(a_copy, b_copy)
    x = x0

    V = m + n - 1   # numarul de celule bazice necesar

    # Tratare degenerare: daca NC < V, adaugam celule cu valoare 0
    if len(J) < V:
        all_cells = {(i, j) for i in range(m) for j in range(n)}
        J_set = set(J)
        for cell in all_cells:
            if len(J) >= V:
                break
            if cell not in J_set:
                J.append(cell)
                J_set.add(cell)
                # x[cell] ramane 0

    f0 = cost_total(x, c, J)

    iterations = []

    # Snapshot initial
    snap0 = _make_snap(0, x, c, J, a, b, m, n, f0, None, None, None, 'continue', "Solutie initiala N-V")
    iterations.append(snap0)

    MAX_ITER = 500
    for k in range(1, MAX_ITER + 1):
        # PAS 4 – multiplicatori u, v
        u, v = calculeaza_uv(c, J, m, n)

        # PAS 5 – delta
        delta = calculeaza_delta(c, u, v, J, m, n)

        # PAS 5 – Test optimalitate
        neg_deltas = {cell: d for cell, d in delta.items() if d < 0}

        if not neg_deltas:
            # Solutie optima
            snap = _make_snap(k, x, c, J, a, b, m, n,
                              cost_total(x, c, J),
                              u, v, delta, 'optimal',
                              "Toate delta >= 0  =>  OPTIM")
            iterations.append(snap)
            break

        # PAS 6 – selectia celulei intrate in baza
        pq = min(neg_deltas, key=lambda cell: neg_deltas[cell])
        p, q = pq

        # PAS 7 – gasim circuitul
        circuit = gaseste_circuit_v2(p, q, J)
        if circuit is None:
            snap = _make_snap(k, x, c, J, a, b, m, n,
                              cost_total(x, c, J),
                              u, v, delta, 'error',
                              f"Nu s-a putut gasi circuit pentru ({p+1},{q+1})")
            iterations.append(snap)
            return {'status': 'error', 'iterations': iterations,
                    'fictiva_sursa': fictiva_sursa, 'fictiva_dest': fictiva_dest,
                    'm_orig': m_orig, 'n_orig': n_orig, 'm': m, 'n': n}

        # circuit[0] == circuit[-1] == (p,q)  =>  ranguri: 0=par, 1=impar, ...
        # celule de rang impar: circuit[1], circuit[3], ...
        rang_impar = [circuit[idx] for idx in range(1, len(circuit)-1, 2)]
        rang_par   = [circuit[idx] for idx in range(2, len(circuit)-1, 2)]

        # PAS 8 – theta
        theta = min(x[i][j] for (i, j) in rang_impar)

        snap = _make_snap(k, x, c, J, a, b, m, n,
                          cost_total(x, c, J),
                          u, v, delta, 'continue',
                          f"delta[{p+1},{q+1}]={fmt(neg_deltas[pq])}  |  theta={fmt(theta)}",
                          circuit=circuit, pq=pq, theta=theta)
        iterations.append(snap)

        # Actualizam x
        x[p][q] = theta
        for (i, j) in rang_par:
            x[i][j] = x[i][j] + theta
        for (i, j) in rang_impar:
            x[i][j] = x[i][j] - theta

        # Actualizam J: (p,q) intra, celula cu x==0 iese
        iesita = None
        for (i, j) in rang_impar:
            if x[i][j] == F(0):
                iesita = (i, j)
                break
        if iesita is None:
            iesita = rang_impar[0]

        J_set = set(J)
        J_set.discard(iesita)
        J_set.add((p, q))
        J = list(J_set)

    else:
        return {'status': 'error', 'iterations': iterations,
                'fictiva_sursa': fictiva_sursa, 'fictiva_dest': fictiva_dest,
                'm_orig': m_orig, 'n_orig': n_orig, 'm': m, 'n': n}

    return {
        'status'        : 'optimal',
        'iterations'    : iterations,
        'x_opt'         : x,
        'f_opt'         : cost_total(x, c, J),
        'fictiva_sursa' : fictiva_sursa,
        'fictiva_dest'  : fictiva_dest,
        'm_orig'        : m_orig,
        'n_orig'        : n_orig,
        'm'             : m,
        'n'             : n,
        'a'             : a,
        'b'             : b,
        'c'             : c,
        'J_opt'         : J,
    }


def _make_snap(k, x, c, J, a, b, m, n, fk,
               u, v, delta, status, msg,
               circuit=None, pq=None, theta=None):
    return {
        'k'      : k,
        'x'      : [row[:] for row in x],
        'c'      : [row[:] for row in c],
        'J'      : list(J),
        'a'      : list(a),
        'b'      : list(b),
        'm'      : m,
        'n'      : n,
        'fk'     : fk,
        'u'      : list(u) if u else None,
        'v'      : list(v) if v else None,
        'delta'  : dict(delta) if delta else None,
        'status' : status,
        'msg'    : msg,
        'circuit': circuit,
        'pq'     : pq,
        'theta'  : theta,
    }


# ============================================================
#  Constructia textului pentru un snapshot (iteratie)
# ============================================================
def build_snap_text(snap, fictiva_sursa, fictiva_dest, m_orig, n_orig):
    m = snap['m']
    n = snap['n']
    x = snap['x']
    c = snap['c']
    J = set(snap['J'])
    a = snap['a']
    b = snap['b']
    fk = snap['fk']
    u = snap['u']
    v = snap['v']
    delta = snap['delta']
    k = snap['k']
    circuit = snap['circuit']
    pq = snap['pq']
    theta = snap['theta']

    linii = []

    # ---- Header iteratie ----
    total_w = 70
    linii.append(f"\n  ╔{'='*total_w}╗")
    linii.append(f"  ║   ITERATIA  I_{k}   —   {snap['msg']}".ljust(total_w+4) + "║")
    linii.append(f"  ╚{'='*total_w}╝\n")

    # ---- Tabelul de transport ----
    # Latimi coloane
    CW = 8  # latime celula

    def cell(val, w=CW):
        return str(val).center(w)

    # etichete surse/destinatii
    src_lbl = [f"A{i+1}" for i in range(m)]
    dst_lbl = [f"B{j+1}" for j in range(n)]
    if fictiva_sursa:
        src_lbl[-1] = f"A{m}*"
    if fictiva_dest:
        dst_lbl[-1] = f"B{n}*"

    # header coloana
    hdr = "  " + "A\\B".center(6)
    for j in range(n):
        hdr += cell(dst_lbl[j])
    hdr += cell("D", 6)
    linii.append(hdr)
    linii.append("  " + "-" * (6 + n * CW + 6))

    for i in range(m):
        row_str = f"  {src_lbl[i].center(6)}"
        for j in range(n):
            xval = fmt(x[i][j]) if x[i][j] != F(0) or (i, j) in J else "·"
            cval = fmt(c[i][j])
            # format celula: xij sus, cij dreapta-sus mic
            if (i, j) in J:
                marker = "►" if pq == (i, j) else " "
                cell_str = f"{marker}{xval}/{cval}".center(CW)
            else:
                cell_str = f"[{cval}]".center(CW)
            row_str += cell_str
        row_str += cell(fmt(a[i]), 6)
        linii.append(row_str)

    # rand necesare
    linii.append("  " + "-" * (6 + n * CW + 6))
    nec_str = "  " + "N".center(6)
    for j in range(n):
        nec_str += cell(fmt(b[j]))
    linii.append(nec_str)
    linii.append("")

    # ---- Costul curent ----
    linii.append(f"  f_k = {fmt(fk)}")
    linii.append("")

    # ---- Componente bazice / nebazice ----
    bazice  = sorted(J)
    nebazice = [(i, j) for i in range(m) for j in range(n) if (i, j) not in J]
    linii.append(f"  Celule bazice  (NC = {len(bazice)},  V = m+n-1 = {m}+{n}-1 = {m+n-1}):")
    linii.append("  " + "  ".join(f"x{i+1}{j+1}={fmt(x[i][j])}" for (i,j) in bazice))
    linii.append("")

    # ---- Sistemul S si multiplicatorii u, v ----
    if u is not None:
        linii.append("  Sistemul S  (u[i] + v[j] = c[i][j]  pentru (i,j) bazice):")
        linii.append(f"  u[1] = 0  (conventie)")
        for (i, j) in bazice:
            linii.append(f"    u{i+1} + v{j+1} = c{i+1}{j+1} = {fmt(c[i][j])}")
        linii.append("")
        u_str = "  ".join(f"u{i+1}={fmt(u[i])}" for i in range(m))
        v_str = "  ".join(f"v{j+1}={fmt(v[j])}" for j in range(n))
        linii.append(f"  => {u_str}")
        linii.append(f"     {v_str}")
        linii.append("")

    # ---- Tabelul costurilor modificate c~ij ----
    if u is not None and v is not None:
        linii.append("  Tabel c~[i][j] = u[i] + v[j]  si  delta[i][j] = c[i][j] - c~[i][j]:")
        # header
        ch_hdr = "  " + "c~\\Δ".center(6)
        for j in range(n):
            ch_hdr += dst_lbl[j].center(CW)
        linii.append(ch_hdr)
        linii.append("  " + "-" * (6 + n * CW))
        for i in range(m):
            row_s = f"  {src_lbl[i].center(6)}"
            for j in range(n):
                if (i, j) in J:
                    row_s += "  ·  ".center(CW)
                else:
                    d = delta.get((i, j), F(0))
                    ctilde = u[i] + v[j]
                    row_s += f"{fmt(ctilde)}/{fmt(d)}".center(CW)
            linii.append(row_s)
        linii.append("")

    # ---- Criteriul de optimalitate ----
    if delta is not None:
        neg = [(cell, d) for cell, d in delta.items() if d < F(0)]
        if snap['status'] == 'optimal':
            linii.append("  ✅  Toate delta[i][j] >= 0  =>  Solutia este OPTIMA")
        else:
            linii.append(f"  ❌  Exista {len(neg)} delta < 0  =>  continuam")
            for (ci, cj), d in sorted(neg):
                linii.append(f"      delta[{ci+1},{cj+1}] = {fmt(d)}")

    # ---- Circuit ----
    if circuit is not None and pq is not None:
        p, q = pq
        linii.append("")
        linii.append(f"  Celula intrare in baza: ({p+1},{q+1})  delta={fmt(delta.get(pq, 0))}")
        circ_str = " -> ".join(f"({r+1},{c_+1})" for (r, c_) in circuit)
        linii.append(f"  Circuit: {circ_str}")
        linii.append(f"  theta = {fmt(theta)}")

    linii.append("")
    return "\n".join(linii)


# ============================================================
#  Textul solutiei finale
# ============================================================
def build_sol_text(result):
    if result['status'] != 'optimal':
        return "  ❌  Nu s-a gasit solutia optima."

    m_orig = result['m_orig']
    n_orig = result['n_orig']
    m      = result['m']
    n      = result['n']
    x      = result['x_opt']
    c      = result['c']
    J      = result['J_opt']
    fopt   = result['f_opt']
    fictiva_sursa = result['fictiva_sursa']
    fictiva_dest  = result['fictiva_dest']
    a      = result['a']
    b      = result['b']

    src_lbl = [f"A{i+1}" for i in range(m)]
    dst_lbl = [f"B{j+1}" for j in range(n)]
    if fictiva_sursa:
        src_lbl[-1] = f"A{m}* (fictiva)"
    if fictiva_dest:
        dst_lbl[-1] = f"B{n}* (fictiva)"

    linii = []
    linii.append("=" * 60)
    linii.append(" SOLUTIA OPTIMA A PROBLEMEI DE TRANSPORT")
    linii.append("=" * 60)
    linii.append("")

    # Tabelul solutiei
    CW = 9
    hdr = "  " + "A\\B".center(7)
    for j in range(n):
        hdr += dst_lbl[j].center(CW)
    hdr += "D".center(7)
    linii.append(hdr)
    linii.append("  " + "-" * (7 + n * CW + 7))

    J_set = set(J)
    for i in range(m):
        row_s = f"  {src_lbl[i].center(7)}"
        for j in range(n):
            if (i, j) in J_set and x[i][j] > 0:
                row_s += fmt(x[i][j]).center(CW)
            else:
                row_s += "—".center(CW)
        row_s += fmt(a[i]).center(7)
        linii.append(row_s)

    linii.append("  " + "-" * (7 + n * CW + 7))
    nec = "  " + "N".center(7)
    for j in range(n):
        nec += fmt(b[j]).center(CW)
    linii.append(nec)
    linii.append("")

    # Plan de transport (fara fictive)
    linii.append("-" * 60)
    linii.append(" Plan de transport (cantitati):")
    linii.append("")
    for i in range(m_orig):
        for j in range(n_orig):
            if (i, j) in J_set and x[i][j] > 0:
                linii.append(f"   x{i+1}{j+1} = {fmt(x[i][j])}  "
                             f"  (de la A{i+1} catre B{j+1},"
                             f"  cost unitar c{i+1}{j+1} = {fmt(c[i][j])})")
    linii.append("")

    # Costul total
    linii.append("-" * 60)
    linii.append(" Functia obiectiv:")
    linii.append("")
    terms = []
    for (i, j) in sorted(J_set):
        if i < m_orig and j < n_orig and x[i][j] > 0:
            terms.append(f"c{i+1}{j+1}*x{i+1}{j+1}")
    linii.append(f"  f = " + " + ".join(terms))
    terms_val = []
    total = F(0)
    for (i, j) in sorted(J_set):
        if i < m_orig and j < n_orig and x[i][j] > 0:
            prod = c[i][j] * x[i][j]
            total += prod
            terms_val.append(f"{fmt(c[i][j])}·{fmt(x[i][j])}")
    linii.append(f"  f = " + " + ".join(terms_val))
    linii.append(f"  f_min* = {fmt(fopt)}")
    linii.append("")

    # Verificare
    linii.append("-" * 60)
    linii.append(" Verificare restrictii:")
    linii.append("")
    for i in range(m_orig):
        s = sum(x[i][j] for j in range(n_orig))
        ok = "✅" if s == a[i] else "❌"
        linii.append(f"  {ok}  SUMA_j x{i+1}j = {fmt(s)}  (a{i+1} = {fmt(a[i])})")
    for j in range(n_orig):
        s = sum(x[i][j] for i in range(m_orig))
        ok = "✅" if s == b[j] else "❌"
        linii.append(f"  {ok}  SUMA_i xi{j+1} = {fmt(s)}  (b{j+1} = {fmt(b[j])})")

    if fictiva_sursa:
        linii.append("")
        linii.append(f"  ⚠  S-a adaugat sursa fictiva A{m}* (disponibil = {fmt(a[-1])})")
        linii.append(f"     Destinatiile aprovizionate din A{m}* NU se realizeaza fizic.")
    if fictiva_dest:
        linii.append("")
        linii.append(f"  ⚠  S-a adaugat destinatia fictiva B{n}* (necesar = {fmt(b[-1])})")
        linii.append(f"     Cantitatea transportata la B{n}* reprezinta surplusul nealocat.")

    linii.append("")
    linii.append("=" * 60)
    return "\n".join(linii)
