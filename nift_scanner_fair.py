#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIFT GEOMETRIC RESONANCE SCANNER — FAIR MODE (UNBIASED)
- Scans ALL integers n in 1..N_MAX (no Fibonacci restriction)
- Ranks by |ratio-1| where ratio = TARGET_OBSERVED / defect
- Reports Fibonacci-only results ONLY for contrast (not for selection)
- Saves CSVs using the standard csv module (no pandas required)
- Plots a neighborhood around the best n if matplotlib is available
"""

import math
import csv
import os
from heapq import nsmallest

# =============================== HEADER ===============================
print("="*70)
print("Reference: Non-Equilibrium Informational Field Theory (NIFT) Axioms Foundations of the Universe as a Dissipative Informational Substrate")
print("Author: Yaoharee Lahtee, ORCID: 0009-0005-3861-0626")
print("DOI: 10.5281/zenodo.17674631")
print("="*70)
print("NIFT GEOMETRIC RESONANCE SCANNER — FAIR MODE (UNBIASED)")
print("Target: Identify integers n whose geometric defect matches the Up-Quark scale")
print("="*70)

# ============================== CONSTANTS =============================
PHI = (1 + math.sqrt(5)) / 2
THETA_GOLD = 2 * math.pi / (PHI**2)

# Target scale (dimensionless) to match:
TARGET_OBSERVED = 1.79e-5

# Scan domain and reporting parameters
N_MAX       = 1_000_000   # scan n = 1..N_MAX
TOP_K       = 25          # how many top candidates to list/save
QCD_MIN     = 1.1         # window used for REPORTING only (not for selection)
QCD_MAX     = 1.5
TOL_RATIO   = 0.02        # "near-1" tolerance for a strict closeness test
DEFECT_CAP  = 1e-3        # broad cap to keep table size reasonable

# Output files (CSV)
OUT_ALL = "fair_top_unbiased.csv"
OUT_FIB = "fair_top_fibonacci.csv"

print(f"[-] Golden Ratio (phi) : {PHI:.8f}")
print(f"[-] Golden Angle theta : {THETA_GOLD:.12f} rad")
print(f"[-] Target defect scale: {TARGET_OBSERVED:.2e}")
print(f"[-] Scan domain        : n = 1 .. {N_MAX:,}")
print("-"*70)

# ============================== CORE FUNCS ============================
def defect_for(n: int) -> float:
    """
    defect(n) = | n*THETA_GOLD - 2*pi*k | with k = round(n*THETA_GOLD / (2*pi))
    """
    val = n * THETA_GOLD
    k = round(val / (2 * math.pi))
    return abs(val - 2 * math.pi * k)

def ratio_for(n: int):
    """
    ratio = TARGET_OBSERVED / defect(n)
    """
    d = defect_for(n)
    if d == 0.0:
        return float('inf'), d
    return TARGET_OBSERVED / d, d

# ============================ UNBIASED SCAN ===========================
records = []         # tuples: (abs(ratio-1), n, ratio, defect)
count_close = 0      # count of |ratio-1| <= TOL_RATIO
count_qcd = 0        # count of QCD-window hits (for reporting)
qcd_hits = []        # store first few QCD-window hits

for n in range(1, N_MAX + 1):
    r, d = ratio_for(n)
    if d < DEFECT_CAP:
        err = abs(r - 1.0)
        records.append((err, n, r, d))
        if err <= TOL_RATIO:
            count_close += 1
        if QCD_MIN <= r <= QCD_MAX:
            count_qcd += 1
            # keep a small preview
            if len(qcd_hits) < 10:
                qcd_hits.append((n, r, d))

# Select top-K by closeness to 1
top_unbiased = nsmallest(TOP_K, records, key=lambda x: x[0])

# Argmin (best)
best_err, best_n, best_ratio, best_defect = top_unbiased[0]

# ======================== FIBONACCI (CONTRAST) ========================
# Follow original script's Fibonacci start (F3 onward): 1, 2, 3, 5, ...
fibs = []
a, b = 1, 2
idx = 3
while b <= N_MAX:
    fibs.append((b, idx))  # (n, F-index)
    a, b = b, a + b
    idx += 1

fib_records = []
for n_fib, fidx in fibs:
    r, d = ratio_for(n_fib)
    fib_records.append((abs(r - 1.0), n_fib, r, d, f"F{fidx}"))

top_fib = nsmallest(min(TOP_K, len(fib_records)), fib_records, key=lambda x: x[0])

# =============================== REPORT ===============================
print(">>> UNBIASED RESULT (argmin of |ratio-1| over all n):")
print(f"    n* = {int(best_n):,}")
print(f"    ratio(n*) = {best_ratio:.6f}")
print(f"    defect(n*)= {best_defect:.3e}")
print(f"    count with |ratio-1| <= {TOL_RATIO:.0%} : {count_close:,} (within 1..{N_MAX:,})")
print("-"*70)
print(">>> REPORT on QCD-window counts (NOT a selection rule in FAIR mode):")
print(f"    window [{QCD_MIN:.1f}, {QCD_MAX:.1f}] #hits = {count_qcd:,}")
for j,(nq, rq, dq) in enumerate(qcd_hits, start=1):
    print(f"      {j:>2}) n={nq:,}, ratio={rq:.6f}, defect={dq:.3e}")
print("-"*70)

# ============================== SAVE CSVs =============================
def save_unbiased_csv(path: str, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["abs(ratio-1)", "n", "ratio", "defect"])
        for err, n, r, d in rows:
            w.writerow([f"{err:.12g}", n, f"{r:.12g}", f"{d:.12g}"])

def save_fib_csv(path: str, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["abs(ratio-1)", "n", "ratio", "defect", "layer"])
        for err, n, r, d, layer in rows:
            w.writerow([f"{err:.12g}", n, f"{r:.12g}", f"{d:.12g}", layer])

save_unbiased_csv(OUT_ALL, top_unbiased)
save_fib_csv(OUT_FIB, top_fib)

print("Files saved:")
print(f" - {os.path.abspath(OUT_ALL)}")
print(f" - {os.path.abspath(OUT_FIB)}")

# ============================== OPTIONAL PLOT =========================
# Plot a single neighborhood around the best n (if matplotlib is available)
try:
    import matplotlib.pyplot as plt
    import numpy as np

    W = 3000  # half-width of window
    lo = max(1, int(best_n) - W)
    hi = min(N_MAX, int(best_n) + W)

    ns = np.arange(lo, hi + 1, dtype=int)
    ratios = []
    for nn in ns:
        rr, dd = ratio_for(nn)
        ratios.append(rr)

    plt.figure()
    plt.plot(ns, ratios)
    plt.axhline(1.0)
    plt.title(f"Ratio vs n around best n={int(best_n)}")
    plt.xlabel("n")
    plt.ylabel("ratio = TARGET_OBSERVED / defect")
    plt.tight_layout()
    plt.show()
except Exception as e:
    print("(Plot skipped:", e, ")")
