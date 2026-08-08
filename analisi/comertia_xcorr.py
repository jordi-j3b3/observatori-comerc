"""
Test de correlació creuada amb desfasaments: Indicador Comertia vs ICM de l'INE.

Pregunta: Comertia afirma als seus PDF que el seu indicador "acostuma a funcionar com a
indicador avançat del que posteriorment publiquen l'Idescat i l'INE". Aquest script ho
comprova amb les seves pròpies dades.

Resultat amb dades fins a juliol de 2026 (35 mesos, des de setembre de 2023):
és **coincident, no avançat**. En primeres diferències el màxim de correlació és a k=0
(r=+0,56 amb Espanya nominal, p=0,001) i a k=+1 la correlació cau a zero o a negatiu.
El test de Granger no troba cap aportació de Comertia sobre els retards propis de la
sèrie oficial. El biaix de nivell mitjà contra les sèries nominals és zero: tot el forat
sistemàtic contra les sèries reals (~2 punts) és efecte preus.

Ús: python analisi/comertia_xcorr.py [--refresca]

Notes de mètode
---------------
- Es treballa en **primeres diferències** perquè les dues sèries són variacions
  interanuals: arrosseguen 11 mesos de solapament i una autocorrelació que infla
  qualsevol correlació en nivells. Els resultats en nivells es donen igualment, amb
  els p-valors corregits per mida mostral efectiva (Bartlett/Quenouille).
- Referència catalana: ICM de l'INE **en brut**, no l'ICD CVEC d'Idescat, que no és
  accessible per API en sèrie llarga (veure TODO.md, "ICM per CCAA: sèrie en brut").
  Els resultats forts són els d'Espanya, que és exactament la sèrie que Comertia
  dibuixa als seus gràfics.
- Sense scipy (no és a requirements.txt): els p-valors surten d'una implementació
  pròpia de la t de Student per beta incompleta regularitzada.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data.fetchers import comertia  # noqa: E402

CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "icm.csv")
BRANCA = "Comercio al por menor, excepto de vehículos de motor y motocicletas"
LAGS = range(-6, 7)
MIN_N = 12


# ─── p-valors sense scipy ──────────────────────────────────────────────────
def _betacf(a, b, x):
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            c = 1.0 + aa / c
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Funció beta incompleta regularitzada I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def p_bilateral_t(t, df):
    if df <= 0 or not np.isfinite(t):
        return float("nan")
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    r = float(np.corrcoef(x, y)[0, 1])
    if n <= 2 or abs(r) >= 1:
        return r, n, float("nan")
    t = r * math.sqrt((n - 2) / (1 - r * r))
    return r, n, p_bilateral_t(t, n - 2)


def _acf(x, k):
    x = np.asarray(x, float) - np.mean(x)
    return 1.0 if k == 0 else float(np.sum(x[k:] * x[:-k]) / np.sum(x * x))


def pearson_eff(x, y, maxlag=6):
    """Correlació amb p-valor sobre mida mostral efectiva (sèries autocorrelacionades)."""
    r, n, _ = pearson(x, y)
    s = sum(_acf(x, k) * _acf(y, k) for k in range(1, min(maxlag, n // 4) + 1))
    ne = max(3.0, n / (1 + 2 * s))
    t = r * math.sqrt(max(ne - 2, 1e-9) / max(1 - r * r, 1e-12))
    return r, n, ne, p_bilateral_t(t, ne - 2)


# ─── dades ─────────────────────────────────────────────────────────────────
def carrega_comertia(refresca=False):
    df = comertia.build_serie() if refresca else comertia.load_serie()
    if df.empty:
        df = comertia.build_serie()
    s = df.assign(data=pd.to_datetime(df["data"])).set_index("data")["valor"].sort_index()
    return s


def carrega_icm():
    icm = pd.read_csv(CACHE)
    icm = icm[(icm.indicador == "var_anual") & (icm.branca == BRANCA)]
    icm["data"] = pd.to_datetime(icm["data"])
    return {
        f"{lbl} {tipus}": (icm[(icm.ambit == ambit) & (icm.tipus == tipus)]
                           .set_index("data")["valor"].sort_index())
        for ambit, lbl in (("Cataluña", "Cat"), ("nacional", "ESP"))
        for tipus in ("nominal", "real")
    }


def finestra_contigua(s):
    """Tram contigu més llarg que arriba fins a l'últim mes disponible.

    Els primers anys de la sèrie tenen forats (mesos sense nota de premsa) i el
    2021-2022 està distorsionat per la base covid i per la inflació de dos dígits.
    """
    idx = s.index
    fi = idx.max()
    inici = fi
    while True:
        anterior = inici - pd.DateOffset(months=1)
        if anterior not in idx:
            break
        inici = anterior
    return s.loc[inici:fi]


def desplaça(s, k):
    """Oficial(t+k) reindexat a t, perquè k>0 signifiqui 'Comertia avança k mesos'."""
    out = s.copy()
    out.index = out.index - pd.DateOffset(months=k)
    return out


def taula_xcorr(com, oficials, diferencies):
    a = com.diff().dropna() if diferencies else com
    print(f"{'k':>3} " + "".join(f"{c:>26}" for c in oficials))
    for k in LAGS:
        fila = f"{k:>3} "
        for s in oficials.values():
            b = desplaça(s.diff().dropna() if diferencies else s, k)
            j = pd.concat([a, b], axis=1, join="inner").dropna()
            if len(j) < MIN_N:
                fila += f"{'—':>26}"
                continue
            if diferencies:
                r, n, p = pearson(j.iloc[:, 0], j.iloc[:, 1])
            else:
                r, n, _, p = pearson_eff(j.iloc[:, 0], j.iloc[:, 1])
            fila += f"{f'{r:+.2f} (n={n}, p={p:.3f})':>26}"
        print(fila)


def test_signe(com, oficials):
    dc = com.diff().dropna()
    for lbl, s in oficials.items():
        ds = s.diff().dropna()
        trams = []
        for k in (0, 1):
            j = pd.concat([dc, desplaça(ds, k)], axis=1, join="inner").dropna()
            coincid = (np.sign(j.iloc[:, 0]) == np.sign(j.iloc[:, 1])).mean()
            trams.append(f"k={k}: {coincid * 100:>3.0f}% (n={len(j)})")
        print(f"  {lbl:<14} " + "   ".join(trams))


def test_granger(com, oficials, retards=2):
    for lbl, s in oficials.items():
        j = pd.concat([com.rename("com"), s.rename("off")], axis=1, join="inner").dropna()
        d = pd.DataFrame({"y": j["off"]})
        for i in range(1, retards + 1):
            d[f"o{i}"] = j["off"].shift(i)
            d[f"c{i}"] = j["com"].shift(i)
        d = d.dropna()
        if len(d) < 15:
            print(f"  {lbl:<14} mostra insuficient (n={len(d)})")
            continue
        cols = [f"o{i}" for i in range(1, retards + 1)] + \
               [f"c{i}" for i in range(1, retards + 1)]
        y = d["y"].values
        X = np.column_stack([np.ones(len(d))] + [d[c].values for c in cols])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        dof = len(y) - X.shape[1]
        se = np.sqrt(np.diag((resid @ resid / dof) * np.linalg.inv(X.T @ X)))
        r2 = 1 - (resid @ resid) / np.sum((y - y.mean()) ** 2)
        parts = []
        for i, c in enumerate(cols, start=1):
            if not c.startswith("c"):
                continue
            t = beta[i] / se[i]
            parts.append(f"{c}={beta[i]:+.3f} (t={t:+.2f}, p={p_bilateral_t(t, dof):.3f})")
        print(f"  {lbl:<14} n={len(y)} R2={r2:.2f}  " + "  ".join(parts))


def taula_biaix(com, oficials):
    for lbl, s in oficials.items():
        j = pd.concat([com.rename("com"), s.rename("off")], axis=1, join="inner").dropna()
        d = j["com"] - j["off"]
        print(f"  {lbl:<14} n={len(j)}  biaix mitja {d.mean():+.2f} punts  "
              f"(darrers 12m {d.tail(12).mean():+.2f})  desv. {d.std():.2f}")


def main(refresca=False):
    com = carrega_comertia(refresca)
    oficials = carrega_icm()
    com_w = finestra_contigua(com)
    print(f"Comertia: {len(com_w)} mesos contigus "
          f"{com_w.index.min():%Y-%m} → {com_w.index.max():%Y-%m}  "
          f"(mitjana {com_w.mean():.2f}%, desv. {com_w.std():.2f})")
    ultim_icm = max(s.index.max() for s in oficials.values())
    print(f"ICM de l'INE disponible fins a {ultim_icm:%Y-%m}\n")

    print("=== 1. Correlacio creuada en NIVELLS. r entre Comertia(t) i Oficial(t+k) ===")
    print("k>0 = Comertia avanca l'oficial en k mesos. p corregit per mida efectiva.\n")
    taula_xcorr(com_w, oficials, diferencies=False)

    print("\n=== 2. En PRIMERES DIFERENCIES (treu l'autocorrelacio del interanual) ===\n")
    taula_xcorr(com_w, oficials, diferencies=True)

    print("\n=== 3. Test de signe: coincideix la direccio del canvi mensual? ===")
    test_signe(com_w, oficials)

    print("\n=== 4. Granger: Comertia aporta informacio sobre l'oficial? ===")
    print("Oficial(t) ~ const + 2 retards propis + 2 retards de Comertia\n")
    test_granger(com_w, oficials)

    print("\n=== 5. Nivell: biaix mitja de Comertia sobre cada serie oficial ===")
    taula_biaix(com_w, oficials)


if __name__ == "__main__":
    main(refresca="--refresca" in sys.argv)
