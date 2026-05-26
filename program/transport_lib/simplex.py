import math
import copy
from fractions import Fraction

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont


################ Constante ################

M_Sym = "M" # Simbol pentru M 
M_Val = Fraction(10**7) # Val. numerica pentru M >> 0
INF = math.inf 


###### Functii suport pentru fractii ######

def F(x):
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(x).limit_denominator(10**9)
    except Exception:
        return Fraction(0)

def format_Frac(v, use_M = True):
    if use_M and abs(v) >= M_Val // 2:
        return "+M" if v > 0 else "-M"
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"

def format_Frac_Plain(v):
    if v.denominator == 1:
        return str(int(v))
    return f"{v.numerator}/{v.denominator}"


############ Pas 1 - Standarizare(PL -> PLS) ############

def Standarizare(c, A, b, constraint_types, var_types, opt):

    m = len(b)
    n = len(c)

    c_nou = []
    A_nou = [[] for _ in range(m)]
    var_names = []
    substituii = {}

    # Regula 1: variabilele originale
    for j in range(n):
        vtype = var_types[j] if j < len(var_types) else '>=0'
        if vtype == '>=0':
            c_nou.append(F(c[j]))
            for i in range(m):
                A_nou[i].append(F(A[i][j]))
            var_names.append(f"x{j+1}")
        elif vtype == '<=0':
            c_nou.append(-F(c[j]))
            for i in range(m):
                A_nou[i].append(-F(A[i][j]))
            var_names.append(f"x{j+1}'")
            substituii[j] = ('negativ', len(c_nou)-1)
        elif vtype == 'R':
            c_nou.append(F(c[j]))
            c_nou.append(-F(c[j]))
            for i in range(m):
                A_nou[i].append(F(A[i][j]))
                A_nou[i].append(-F(A[i][j]))
            var_names.append(f"x{j+1}")
            var_names.append(f"x{j+1}'")
            substituii[j] = ('real', len(c_nou)-2, len(c_nou)-1)

    n_original = len(c_nou)

    # Pasul 1: colectam datele pentru fiecare restrictie
    surplus_data = []   # (i, ctype) pentru y-uri
    artif_data   = []   # (i, ctype) pentru z-uri

    y_count = 0
    z_count = 0
    for i in range(m):
        ctype = constraint_types[i]
        if ctype == '<=':
            y_count += 1
            surplus_data.append((i, ctype, y_count, None))
        elif ctype == '>=':
            y_count += 1
            z_count += 1
            surplus_data.append((i, ctype, y_count, z_count))
        elif ctype == '=':
            z_count += 1
            surplus_data.append((i, ctype, None, z_count))

    # Pasul 2: adaugam TOATE y-urile (slack/surplus)
    y_col_map = {}   # i -> index coloana y in c_nou
    z_col_map = {}   # i -> index coloana z in c_nou

    for (i, ctype, yn, zn) in surplus_data:
        if ctype == '<=' and yn is not None:
            c_nou.append(F(0))
            for k in range(m):
                A_nou[k].append(F(1) if k == i else F(0))
            var_names.append(f"y{yn}")
            y_col_map[i] = len(c_nou) - 1
        elif ctype == '>=' and yn is not None:
            c_nou.append(F(0))
            for k in range(m):
                A_nou[k].append(F(-1) if k == i else F(0))
            var_names.append(f"y{yn}")
            y_col_map[i] = len(c_nou) - 1

    # Pasul 3: adaugam TOATE z-urile (artificiale)
    for (i, ctype, yn, zn) in surplus_data:
        if ctype == '>=' and zn is not None:
            penalizare = M_Val if opt == "MIN" else -M_Val
            c_nou.append(F(penalizare))
            for k in range(m):
                A_nou[k].append(F(1) if k == i else F(0))
            var_names.append(f"z{zn}")
            z_col_map[i] = len(c_nou) - 1
        elif ctype == '=' and zn is not None:
            penalizare = M_Val if opt == "MIN" else -M_Val
            c_nou.append(F(penalizare))
            for k in range(m):
                A_nou[k].append(F(1) if k == i else F(0))
            var_names.append(f"z{zn}")
            z_col_map[i] = len(c_nou) - 1

    # Pasul 4: construim baza initiala
    indici_baza = []
    for i in range(m):
        ctype = constraint_types[i]
        if ctype == '<=':
            indici_baza.append(y_col_map[i])
        elif ctype == '>=':
            indici_baza.append(z_col_map[i])
        elif ctype == '=':
            indici_baza.append(z_col_map[i])

    return c_nou, A_nou, [F(x) for x in b], var_names, indici_baza, n_original, substituii


############ Pas 2 - Calcule in Tabel ############

def calculeaza_zk_zj_delta(CB, XB, A, c, m, n):
    zk = sum(CB[i] * XB[i] for i in range(m))
    zj = [sum(CB[i] * A[i][j] for i in range(m)) for j in range(n)]
    delta = [c[j] - zj[j] for j in range(n)]
    return zk, zj, delta

def pivot(A , XB, baza, CB, c , r , q, m , n):
    P = A[r][q]
    XB[r] = XB[r] / P 
    for j in range(n):
        A[r][j] = A[r][j] / P
    for i in range(m):
        if i == r:
            continue
        factor = A[i][q]
        XB[i] = XB[i] - factor * XB[r]
        for j in range(n):
            A[i][j] = A[i][j] - factor * A[r][j]
    baza[r] = q
    CB[r] = c[q]

############ Pas 3 - Afisare Solutie + Verficare ############

def afiseaza_solutie(c_orig, A_orig, b_orig,
                     x_opt, f_opt, opt,
                     var_names_orig, baza_final,
                     XB_final, var_names_pls,
                     A_tab_init, n_original):

    linii = []
    orig_n = len(c_orig)
    m = len(b_orig)
    
    linii.append("=" * 55)
    linii.append(" Solutie optima:")
    linii.append("=" * 55) 

    for j, xv in enumerate(x_opt):
        linii.append(f" x{j+1}* = {format_Frac_Plain(xv)}")

    linii.append("") 
    linii.append("-" * 55) 
    linii.append(f" Functia obiectiv ({opt}):") 
    linii.append(f" f* = {format_Frac_Plain(f_opt)}")
    linii.append("") 

    terms_sym = []
    for j in range(orig_n):
        cj = F(c_orig[j])
        vn = f"x{j+1}"
        cs = format_Frac_Plain(cj)
        terms_sym.append(f"{cs}*{vn}")
    linii.append(f" f = {' +'.join(terms_sym)}")

    terms_val = []
    for j in range(orig_n):
        cj = F(c_orig[j])
        xv = F(x_opt[j])
        cs = format_Frac_Plain(cj)
        xvs = format_Frac_Plain(xv)
        terms_val.append(f"{cs}*{xvs}")
    linii.append(f" f = {' +'.join(terms_val)}")

    produs = []
    total = F(0)
    for j in range(orig_n):
        prod = F(c_orig[j]) * F(x_opt[j])
        produs.append(format_Frac_Plain(prod))
        total += prod
    linii.append(f" f = {' +'.join(produs)}")
    linii.append(f" f_{opt.lower()}* = {format_Frac_Plain(F(f_opt))}")

    linii.append("")
    linii.append("-" * 55)
    linii.append(" Verificare: b = S*Xb")     
    linii.append("")

    n_pls = len(var_names_pls)

    S = []
    for i in range(m):
        row = []
        for bi in baza_final:
            if bi < len(A_tab_init[i]):
                row.append(A_tab_init[i][bi])
            else:
                row.append(F(0))
        S.append(row)

    XB_f = [F(xv) for xv in XB_final]
    b_f = [F(bv) for bv in b_orig]

    Sxb = [sum(S[i][k] * XB_f[k] for k in range(m)) for i in range(m)]

    w_b = max(len(format_Frac_Plain(bv)) for bv in b_f) + 2
    w_s = max( 
        max(len(format_Frac_Plain(S[i][k])) for k in range(m))
            for i in range(m)) + 2
    w_xb = max(len(format_Frac_Plain(XB_f[k])) for k in range(m)) + 2
    w_sxb = max(len(format_Frac_Plain(Sxb[i])) for i in range(m)) + 2

    b_col   = [format_Frac_Plain(bv).center(w_b)   for bv in b_f]
    xb_col  = [format_Frac_Plain(xv).center(w_xb)  for xv in XB_f]
    sxb_col = [format_Frac_Plain(sv).center(w_sxb) for sv in Sxb]

    s_rows = []
    for i in range(m):
        row_str = "  ".join(format_Frac_Plain(S[i][k]).center(w_s) for k in range(m))
        s_rows.append(row_str)
    
    detalii_rows = []
    for i in range(m):
        parts = " + ".join(
            f"{format_Frac_Plain(S[i][k])}·{format_Frac_Plain(XB_f[k])}"
            for k in range(m)
        )
        result = format_Frac_Plain(Sxb[i])
        match  = "✅" if Sxb[i] == b_f[i] else "❌"
        detalii_rows.append(f"  {parts} = {result}  {match}")

    for i in range(m):
        prefix = "(" if i == 0 else ("(" if i == m-1 else "|")
        suffix = ")" if i == 0 else (")" if i == m-1 else "|")
        eq_sign  = "==" if i == m // 2 else "  "
        mul_sign = "·"  if i == m // 2 else " "
        linii.append(
            f"  {prefix}{b_col[i]}{suffix} {eq_sign} "
            f"{prefix}{s_rows[i]}{suffix} {mul_sign} "
            f"{prefix}{xb_col[i]}{suffix}"
        )

    linii.append("")
    linii.append( "Detalii calcul:")
    for dr in detalii_rows:
        linii.append(dr)
    
    all_ok = all(Sxb[i] == b_f[i] for i in range(m))
    linii.append("")
    linii.append(f"  Rezultat verificare: {'✅ CORECT' if all_ok else '❌ EROARE'}")
    linii.append("=" * 55)

    return "\n".join(linii)


############ Algoritm Principal ############

def simplex_primal(c_orig, A_orig, b_orig,
                   constraint_types, var_types, opt='MAX'):

    c_orig_F = [F(x) for x in c_orig]
    A_orig_F = [[F(x) for x in row] for row in A_orig]
    b_orig_F = [F(x) for x in b_orig]

    c, A, b, var_names, baza, n_original, substitutions = Standarizare(
        c_orig_F, A_orig_F, b_orig_F, constraint_types, var_types, opt
    )

    m = len(b)
    n = len(c)

    A_tab      = [row[:] for row in A]
    A_tab_init = [row[:] for row in A]   
    XB         = b[:]
    CB         = [c[baza[i]] for i in range(m)]

    iterations = []  
    MAX_ITER   = 200
    status     = 'optimal'

    for k in range(MAX_ITER + 1):
        zk, zj, delta = calculeaza_zk_zj_delta(CB, XB, A_tab, c, m, n)

        snap = {
            'k'         : k,
            'var_names' : var_names[:],
            'baza'     : baza[:],
            'CB'        : CB[:],
            'XB'        : XB[:],
            'A'         : [row[:] for row in A_tab],
            'c'         : c[:],
            'zk'        : zk,
            'zj'        : zj[:],
            'delta'     : delta[:],
            'pivot_col' : None,
            'pivot_row' : None,
        }

        if opt == 'MAX':
            optimal = all(d <= F(0) for d in delta)
        else:
            optimal = all(d >= F(0) for d in delta)

        if optimal:
            snap['status'] = 'optimal'
            iterations.append(snap)
            break

        if opt == 'MAX':
            candidates = [j for j in range(n) if delta[j] > F(0)]
        else:
            candidates = [j for j in range(n) if delta[j] < F(0)]

        unbounded = any(
            all(A_tab[i][j] <= F(0) for i in range(m))
            for j in candidates
        )
        if unbounded:
            snap['status'] = 'unbounded'
            iterations.append(snap)
            status = 'unbounded'
            break

        if opt == 'MAX':
            q = max(candidates, key=lambda j: delta[j])
        else:
            q = min(candidates, key=lambda j: delta[j])

        ratios = [
            (XB[i] / A_tab[i][q], i)
            for i in range(m) if A_tab[i][q] > F(0)
        ]
        if not ratios:
            snap['status'] = 'unbounded'
            iterations.append(snap)
            status = 'unbounded'
            break

        _, r = min(ratios, key=lambda x: x[0])

        snap['pivot_col'] = q
        snap['pivot_row'] = r
        snap['status']    = 'continue'
        iterations.append(snap)

        pivot(A_tab, XB, baza, CB, c, r, q, m, n)

    else:
        status = 'max_iter'

    x_full = [F(0)] * n
    for i, bi in enumerate(baza):
        x_full[bi] = XB[i]

    x_pls = x_full[:n_original]
    x_opt = []
    pls_idx = 0
    orig_n  = len(c_orig_F)

    for j in range(orig_n):
        vtype = var_types[j] if j < len(var_types) else '>=0'
        if vtype == '>=0':
            x_opt.append(x_pls[pls_idx]);   pls_idx += 1
        elif vtype == '<=0':
            x_opt.append(-x_pls[pls_idx]);  pls_idx += 1
        elif vtype == 'R':
            x_opt.append(x_pls[pls_idx] - x_pls[pls_idx+1]); pls_idx += 2

    zk_final, _, _ = calculeaza_zk_zj_delta(CB, XB, A_tab, c, m, n)

    sol_text = ""
    if status == 'optimal':
        sol_text = afiseaza_solutie(
            c_orig_F, A_orig_F, b_orig_F,
            x_opt, zk_final, opt,
            [f"x{j+1}" for j in range(orig_n)],
            baza, XB, var_names,
            A_tab_init, n_original
        )

    return {
        'status'    : status,
        'iterations': iterations,
        'x_opt'     : x_opt,
        'f_opt'     : zk_final,
        'sol_text'  : sol_text,
        'var_names' : var_names,
        'n_original': n_original,
        'orig_n'    : orig_n,
    }
