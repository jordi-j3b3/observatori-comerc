"""Fetcher del Banco de España: compres amb targeta en terminals de punt de venda (TPV).

Font: Banco de España, Departamento de Sistemas de Pago, a partir de les dades del
Sistema de Tarjetas y Medios de Pago (STMP). Excel amb adreça fixa:
  https://www.bde.es/webbe/es/estadisticas/compartido/datos/xlsx/tarjetas1.xlsx
Full "Datos trimestrales": període ('2026 T2'), operacions (milers), % variació
interanual, imports (milions d'euros), % variació interanual. Des de 2005 T1.

Abast: targetes emeses per entitats de les xarxes espanyoles, en terminals situats a
Espanya. Totes les activitats (comerç, restauració, carburants...): NO és CNAE 47,
és context del consum pagat amb targeta. Total nacional, sense sectors ni territori.
"""
import io
import re

import pandas as pd
import requests

URL_TARGETES = "https://www.bde.es/webbe/es/estadisticas/compartido/datos/xlsx/tarjetas1.xlsx"
HEADERS = {"User-Agent": "Mozilla/5.0 (J3B3 Observatori; +https://www.j3b3.com)"}


def fetch_targetes_tpv():
    """Retorna un DataFrame trimestral amb operacions, import i tiquet mitjà.

    Columnes: periode ('2026T2'), any, trimestre, data (darrer dia del trimestre),
    operacions_milers, import_milions, tiquet_mitja_eur, var_operacions, var_import,
    var_tiquet (variacions interanuals en %).
    Les variacions es calculen sobre els nivells i es contrasten amb les que publica
    el BdE; si no quadren, es llança error (el processador manté la cache).
    """
    r = requests.get(URL_TARGETES, headers=HEADERS, timeout=60)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Datos trimestrales", header=None)

    files = []
    for _, fila in raw.iterrows():
        m = re.fullmatch(r"(\d{4}) T([1-4])", str(fila[0]).strip())
        if not m or pd.isna(fila[1]) or pd.isna(fila[3]):
            continue
        files.append({
            "any": int(m.group(1)), "trimestre": int(m.group(2)),
            "operacions_milers": float(fila[1]), "import_milions": float(fila[3]),
            "var_operacions_bde": None if pd.isna(fila[2]) else float(fila[2]) * 100,
            "var_import_bde": None if pd.isna(fila[4]) else float(fila[4]) * 100,
        })
    if not files:
        raise ValueError("l'Excel del BdE no té el format esperat (cap fila 'AAAA Tn')")

    df = pd.DataFrame(files).sort_values(["any", "trimestre"]).reset_index(drop=True)
    df["periode"] = df["any"].astype(str) + "T" + df["trimestre"].astype(str)
    df["data"] = [pd.Period(f"{a}Q{q}", freq="Q").end_time.strftime("%Y-%m-%d")
                  for a, q in zip(df["any"], df["trimestre"])]
    df["tiquet_mitja_eur"] = df["import_milions"] * 1e6 / (df["operacions_milers"] * 1e3)
    for col, nom in [("operacions_milers", "operacions"), ("import_milions", "import"),
                     ("tiquet_mitja_eur", "tiquet")]:
        df[f"var_{nom}"] = (df[col] / df[col].shift(4) - 1) * 100

    # Les sèries han de ser trimestres consecutius per poder fer el shift(4)
    seq = df["any"] * 4 + df["trimestre"]
    if not (seq.diff().dropna() == 1).all():
        raise ValueError("la sèrie trimestral del BdE té forats")
    for nom in ("operacions", "import"):
        bde = df[f"var_{nom}_bde"]
        dif = (df[f"var_{nom}"] - bde).abs()[bde.notna()]
        if (dif > 0.05).any():
            raise ValueError(f"la variació de {nom} calculada no quadra amb la del BdE")

    return df[["periode", "any", "trimestre", "data", "operacions_milers", "import_milions",
               "tiquet_mitja_eur", "var_operacions", "var_import", "var_tiquet"]]
