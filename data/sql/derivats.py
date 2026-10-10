"""
Indicadors derivats: creuaments entre fonts calculats al motor.

El xatbot no fa càlculs: llegeix aquestes sèries, que ja porten la fórmula, les
sèries d'origen i els avisos de qualitat heretats. migrate.py les construeix
després de les sèries de base, llegint-les de DuckDB per les claus comunes
(geo_codi, cnae_codi), de manera que un creuament no depèn de cap etiqueta de text.

Cada derivat és un dict amb serie_id, name, description, formula, fonts_origen,
unit, frequency i build(con) -> DataFrame amb date, value, dim_1..3, geo_codi,
cnae_codi i avis.
"""
import pandas as pd

_COLS = ["date", "value", "dim_1", "dim_2", "dim_3", "geo_codi", "cnae_codi", "avis"]


def _obs(con, serie_id, where="", params=()):
    df = con.execute(f"""
        SELECT date, value, dim_1, dim_2, dim_3, geo_codi, cnae_codi, avis
        FROM observations WHERE serie_id = ? {where}
    """, [serie_id, *params]).df()
    df["date"] = pd.to_datetime(df["date"])
    return df


def _uneix_avis(*cols, extra=None):
    """Unió fila a fila de llistes de codis d'avís ('a,b'), més els codis extra."""
    def _una(vals):
        codis = set(extra or [])
        for v in vals:
            if isinstance(v, str) and v:
                codis.update(v.split(","))
        return ",".join(sorted(codis)) or None
    return [_una(vals) for vals in zip(*cols)]


def _ipc_anual(con):
    """IPC general, mitjana anual (base 2021 = 100). Només anys complets."""
    ipc = _obs(con, "ipc")
    ipc["any"] = ipc["date"].dt.year
    g = ipc.groupby("any")["value"].agg(["mean", "count"])
    return g.loc[g["count"] == 12, "mean"].rename("ipc")


def _surt(df, **fixes):
    df = df.copy()
    for k, v in fixes.items():
        df[k] = v
    for c in _COLS:
        if c not in df.columns:
            df[c] = None
    return df.dropna(subset=["value"])[_COLS]


# ─── EEE per CCAA: rendiment per local, per ocupat i per habitant ────────────

def _eee(con, col):
    df = _obs(con, f"eee_ccaa_{col}")
    df["any"] = df["date"].dt.year
    return df[["date", "any", "geo_codi", "value", "avis"]].rename(
        columns={"value": col, "avis": f"avis_{col}"})


def _build_per_local_real(con):
    df = _eee(con, "xifra_negoci").merge(_eee(con, "locals"), on=["date", "any", "geo_codi"])
    df = df.merge(_ipc_anual(con), left_on="any", right_index=True)
    df["value"] = df["xifra_negoci"] / df["locals"] / (df["ipc"] / 100)
    df["avis"] = _uneix_avis(df["avis_xifra_negoci"], df["avis_locals"],
                             extra=["deflactor_general"])
    return _surt(df, cnae_codi="47")


def _build_ocupats_per_local(con):
    df = _eee(con, "personal_ocupat").merge(_eee(con, "locals"), on=["date", "any", "geo_codi"])
    df["value"] = df["personal_ocupat"] / df["locals"]
    df["avis"] = _uneix_avis(df["avis_personal_ocupat"], df["avis_locals"])
    return _surt(df, cnae_codi="47")


def _build_per_ocupat_real(con):
    df = _eee(con, "xifra_negoci").merge(_eee(con, "personal_ocupat"),
                                          on=["date", "any", "geo_codi"])
    df = df.merge(_ipc_anual(con), left_on="any", right_index=True)
    df["value"] = df["xifra_negoci"] / df["personal_ocupat"] / (df["ipc"] / 100)
    df["avis"] = _uneix_avis(df["avis_xifra_negoci"], df["avis_personal_ocupat"],
                             extra=["deflactor_general"])
    return _surt(df, cnae_codi="47")


def _build_per_habitant_real(con):
    pob = _obs(con, "empreses_poblacio")
    pob = pob[["date", "geo_codi", "value", "avis"]].rename(
        columns={"value": "poblacio", "avis": "avis_pob"})
    df = _eee(con, "xifra_negoci").merge(pob, on=["date", "geo_codi"])
    df = df.merge(_ipc_anual(con), left_on="any", right_index=True)
    df["value"] = df["xifra_negoci"] / df["poblacio"] / (df["ipc"] / 100)
    df["avis"] = _uneix_avis(df["avis_xifra_negoci"], df["avis_pob"],
                             extra=["deflactor_general"])
    return _surt(df, cnae_codi="47")


# ─── ICM: preus implícits, productivitat, mitjanes anuals ────────────────────

def _icm_index(con, tipus, geo="pais:ES"):
    w = "AND dim_3 = 'index'"
    params = ()
    if geo is not None:
        w += " AND geo_codi = ?"
        params = (geo,)
    df = _obs(con, f"icm_{tipus}", w, params)
    return df[["date", "geo_codi", "cnae_codi", "value", "avis"]].rename(
        columns={"value": tipus, "avis": f"avis_{tipus}"})


def _yoy(df, col, claus):
    """Variació interanual (%) d'una columna mensual, per grup de claus."""
    df = df.sort_values("date")
    prev = df[[*claus, "date", col]].copy()
    prev["date"] = prev["date"] + pd.DateOffset(years=1)
    prev = prev.rename(columns={col: f"{col}_prev"})
    out = df.merge(prev, on=[*claus, "date"], how="left")
    out[f"{col}_yoy"] = (out[col] / out[f"{col}_prev"] - 1) * 100
    return out


def _deflactor(con):
    df = _icm_index(con, "nominal").merge(_icm_index(con, "real"),
                                          on=["date", "geo_codi", "cnae_codi"])
    df["deflactor"] = df["nominal"] / df["real"] * 100
    df["avis"] = _uneix_avis(df["avis_nominal"], df["avis_real"])
    return df


def _build_deflactor(con):
    df = _deflactor(con)
    df["value"] = df["deflactor"]
    return _surt(df)


# Branca de l'ICM -> grup de l'IPC que en mesura els preus de consum.
_PARELLES_IPC = {
    "47": "Índex general",
    "47_ALIM": "Alimentació i begudes no alcohòliques",
    "47_EQPERS": "Vestit i calçat",
    "47_EQLLAR": "Parament de la llar",
}


def _build_deflactor_vs_ipc(con):
    d = _yoy(_deflactor(con), "deflactor", ["geo_codi", "cnae_codi"])
    d = d[d["cnae_codi"].isin(_PARELLES_IPC)].copy()
    d["grup"] = d["cnae_codi"].map(_PARELLES_IPC)
    ipc = _obs(con, "ipc_coicop")[["date", "dim_1", "value", "geo_codi"]].rename(
        columns={"dim_1": "grup", "value": "ipc"})
    ipc = _yoy(ipc, "ipc", ["grup", "geo_codi"])
    df = d.merge(ipc[["date", "grup", "geo_codi", "ipc_yoy"]], on=["date", "grup", "geo_codi"])
    df["value"] = df["deflactor_yoy"] - df["ipc_yoy"]
    df["dim_1"] = df["grup"]
    return _surt(df)


def _build_productivitat(con):
    df = _icm_index(con, "real").merge(_icm_index(con, "ocupacio"),
                                       on=["date", "geo_codi", "cnae_codi"])
    df["prod"] = df["real"] / df["ocupacio"]
    df = _yoy(df, "prod", ["geo_codi", "cnae_codi"])
    df["value"] = df["prod_yoy"]
    df["avis"] = _uneix_avis(df["avis_real"], df["avis_ocupacio"])
    return _surt(df)


def _build_icm_mitjana_anual(tipus):
    def _build(con):
        df = _icm_index(con, tipus, geo=None)
        df["any"] = df["date"].dt.year
        g = (df.groupby(["geo_codi", "cnae_codi", "any"])
               .agg(mitjana=(tipus, "mean"), mesos=(tipus, "count"),
                    avis=(f"avis_{tipus}", "first"))
               .reset_index())
        g = g[g["mesos"] == 12]
        prev = g[["geo_codi", "cnae_codi", "any", "mitjana"]].copy()
        prev["any"] += 1
        g = g.merge(prev, on=["geo_codi", "cnae_codi", "any"], suffixes=("", "_prev"))
        g["value"] = (g["mitjana"] / g["mitjana_prev"] - 1) * 100
        g["date"] = pd.to_datetime(dict(year=g["any"], month=1, day=1))
        return _surt(g)
    return _build


# ─── ICM per modes de distribució ────────────────────────────────────────────

def _build_modes_relatiu(con):
    df = _obs(con, "icm_distribucio_real", "AND dim_2 = 'index'")
    base = df[df["dim_1"] == "Empresas unilocalizadas"][["date", "value"]].rename(
        columns={"value": "base"})
    df = df[~df["dim_1"].isin(["Empresas unilocalizadas", "General"])].merge(base, on="date")
    df["value"] = df["value"] / df["base"] * 100
    return _surt(df[["date", "value", "dim_1", "geo_codi", "cnae_codi", "avis"]])


# ─── Canal online i pagaments ────────────────────────────────────────────────

def _build_ecommerce_pes(con):
    ec = _obs(con, "ecommerce_cnae47")[["date", "value", "avis"]].rename(
        columns={"value": "ec", "avis": "avis_ec"})
    xn = _obs(con, "eee_ccaa_xifra_negoci", "AND geo_codi = 'pais:ES'")
    xn = xn[["date", "value", "avis"]].rename(columns={"value": "xn", "avis": "avis_xn"})
    df = ec.merge(xn, on="date")
    df["value"] = df["ec"] / df["xn"] * 100
    df["avis"] = _uneix_avis(df["avis_ec"], df["avis_xn"], extra=["abast_diferent"])
    return _surt(df, geo_codi="pais:ES", cnae_codi="47")


def _build_tpv_menys_icm(con):
    tpv = _obs(con, "targetes_tpv_var_import")[["date", "value", "avis"]].rename(
        columns={"value": "tpv", "avis": "avis_tpv"})
    tpv["trim"] = tpv["date"].dt.to_period("Q")
    icm = _icm_index(con, "nominal")
    icm = icm[icm["cnae_codi"] == "47"].copy()
    icm["trim"] = icm["date"].dt.to_period("Q")
    q = (icm.groupby("trim").agg(idx=("nominal", "mean"), mesos=("nominal", "count"),
                                  avis_icm=("avis_nominal", "first")).reset_index())
    q = q[q["mesos"] == 3]
    prev = q[["trim", "idx"]].copy()
    prev["trim"] = prev["trim"] + 4
    q = q.merge(prev, on="trim", suffixes=("", "_prev"))
    q["icm_yoy"] = (q["idx"] / q["idx_prev"] - 1) * 100
    df = tpv.merge(q[["trim", "icm_yoy", "avis_icm"]], on="trim")
    df["value"] = df["tpv"] - df["icm_yoy"]
    df["avis"] = _uneix_avis(df["avis_tpv"], df["avis_icm"])
    return _surt(df, geo_codi="pais:ES")


# ─── Registre ────────────────────────────────────────────────────────────────

DERIVATS = [
    dict(serie_id="der_vendes_per_local_real",
         name="Vendes per local (euros de 2021)",
         description="Xifra de negoci del comerç al detall dividida pel nombre de locals, "
                     "per CCAA, a preus de 2021.",
         formula="eee_ccaa_xifra_negoci / eee_ccaa_locals / (IPC general mitjana anual / 100)",
         fonts_origen="eee_ccaa_xifra_negoci, eee_ccaa_locals, ipc",
         unit="EUR de 2021 per local", frequency="annual",
         build=_build_per_local_real),
    dict(serie_id="der_ocupats_per_local",
         name="Persones ocupades per local",
         description="Personal ocupat del comerç al detall per local, per CCAA.",
         formula="eee_ccaa_personal_ocupat / eee_ccaa_locals",
         fonts_origen="eee_ccaa_personal_ocupat, eee_ccaa_locals",
         unit="persones per local", frequency="annual",
         build=_build_ocupats_per_local),
    dict(serie_id="der_vendes_per_ocupat_real",
         name="Vendes per persona ocupada (euros de 2021)",
         description="Xifra de negoci del comerç al detall per persona ocupada, per CCAA, "
                     "a preus de 2021.",
         formula="eee_ccaa_xifra_negoci / eee_ccaa_personal_ocupat / (IPC general / 100)",
         fonts_origen="eee_ccaa_xifra_negoci, eee_ccaa_personal_ocupat, ipc",
         unit="EUR de 2021 per persona", frequency="annual",
         build=_build_per_ocupat_real),
    dict(serie_id="der_vendes_per_habitant_real",
         name="Vendes del comerç al detall per habitant (euros de 2021)",
         description="Xifra de negoci del comerç al detall per habitant, per CCAA, a preus "
                     "de 2021. Mesura on es ven, no on viuen els compradors: les "
                     "comunitats turístiques o amb centralitat comercial en surten altes.",
         formula="eee_ccaa_xifra_negoci / empreses_poblacio / (IPC general / 100)",
         fonts_origen="eee_ccaa_xifra_negoci, empreses_poblacio, ipc",
         unit="EUR de 2021 per habitant", frequency="annual",
         build=_build_per_habitant_real),
    dict(serie_id="der_icm_deflactor_implicit",
         name="Preus implícits de les vendes del comerç per branca",
         description="Deflactor implícit de l'ICM (índex nominal sobre índex real), per "
                     "branca, a escala estatal. Aproxima l'evolució dels preus del que es "
                     "ven a cada branca.",
         formula="icm_nominal[index] / icm_real[index] * 100",
         fonts_origen="icm_nominal, icm_real",
         unit="índex (base 2021 = 100)", frequency="monthly",
         build=_build_deflactor),
    dict(serie_id="der_icm_deflactor_vs_ipc",
         name="Preus de venda del comerç contra IPC del grup",
         description="Diferència entre la variació interanual del deflactor implícit de "
                     "l'ICM d'una branca i la de l'IPC del grup de consum corresponent. "
                     "Positiu: els preus del que ven el comerç pugen més que l'IPC del grup.",
         formula="var. interanual der_icm_deflactor_implicit - var. interanual ipc_coicop "
                 "(47-general, 47_ALIM-alimentació, 47_EQPERS-vestit i calçat, "
                 "47_EQLLAR-parament de la llar)",
         fonts_origen="icm_nominal, icm_real, ipc_coicop",
         unit="punts percentuals", frequency="monthly",
         build=_build_deflactor_vs_ipc),
    dict(serie_id="der_icm_productivitat_var_anual",
         name="Productivitat aparent mensual (variació interanual)",
         description="Variació interanual de les vendes reals per persona ocupada, a partir "
                     "dels índexs de l'ICM. L'INE només publica l'ocupació de l'ICM per al "
                     "total, el total sense estacions de servei i les estacions de servei.",
         formula="var. interanual de (icm_real[index] / icm_ocupacio[index])",
         fonts_origen="icm_real, icm_ocupacio",
         unit="% variació interanual", frequency="monthly",
         build=_build_productivitat),
    dict(serie_id="der_icm_real_var_anual",
         name="Vendes reals, variació de la mitjana anual",
         description="Variació de la mitjana anual de l'índex real de l'ICM, per branca i "
                     "CCAA. Només anys complets.",
         formula="mitjana anual de icm_real[index] / mitjana de l'any anterior - 1",
         fonts_origen="icm_real",
         unit="% variació anual", frequency="annual",
         build=_build_icm_mitjana_anual("real")),
    dict(serie_id="der_icm_nominal_var_anual",
         name="Vendes nominals, variació de la mitjana anual",
         description="Variació de la mitjana anual de l'índex nominal de l'ICM, per branca "
                     "i CCAA. Només anys complets.",
         formula="mitjana anual de icm_nominal[index] / mitjana de l'any anterior - 1",
         fonts_origen="icm_nominal",
         unit="% variació anual", frequency="annual",
         build=_build_icm_mitjana_anual("nominal")),
    dict(serie_id="der_icm_modes_relatiu",
         name="Vendes reals per mode de distribució, relatives a les empreses d'un local",
         description="Índex real de cada mode de distribució dividit pel de les empreses "
                     "d'un sol local. Per sobre de 100: el mode ha crescut més que el petit "
                     "comerç des del 2021.",
         formula="icm_distribucio_real[mode, index] / icm_distribucio_real[Empresas "
                 "unilocalizadas, index] * 100",
         fonts_origen="icm_distribucio_real",
         unit="índex (2021: unilocalitzades = 100)", frequency="monthly",
         build=_build_modes_relatiu),
    dict(serie_id="der_ecommerce_pes_vendes",
         name="Pes del comerç electrònic sobre les vendes del comerç al detall",
         description="Facturació en comerç electrònic del CNAE 47 (CNMC) sobre la xifra de "
                     "negoci del comerç al detall (INE). Ordre de magnitud: les dues fonts "
                     "no mesuren el mateix univers.",
         formula="ecommerce_cnae47 / eee_ccaa_xifra_negoci[pais:ES] * 100",
         fonts_origen="ecommerce_cnae47, eee_ccaa_xifra_negoci",
         unit="% de la xifra de negoci", frequency="annual",
         build=_build_ecommerce_pes),
    dict(serie_id="der_tpv_menys_icm",
         name="Pagaments amb targeta contra vendes del comerç",
         description="Variació interanual de l'import pagat amb targeta en TPV menys la de "
                     "l'ICM nominal (mitjana trimestral). Positiu: la targeta creix més que "
                     "les vendes del comerç, per substitució de l'efectiu o per despesa "
                     "fora del comerç.",
         formula="targetes_tpv_var_import - var. interanual de la mitjana trimestral de "
                 "icm_nominal[47, index]",
         fonts_origen="targetes_tpv_var_import, icm_nominal",
         unit="punts percentuals", frequency="quarterly",
         build=_build_tpv_menys_icm),
]
