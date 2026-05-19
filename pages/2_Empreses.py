"""Pàgina 2: Empreses del comerç al detall (CNAE 47).

Estructura reduïda (pilot Fase 2 — reducció frontend):
  TÍTOL · SUBTÍTOL CURT · LECTURA VIGENT · KPI ÚNIC · GRÀFIC NACIONAL · MAPA CCAA
  + 2 expanders ("Veure més detall", "Metodologia i fonts") + descàrrega CSV.

La reducció afecta només el frontend: el CSV i la lògica analítica romanen
intactes; el detall que surt del cos visible queda accessible via expanders i
via el CSV per a l'agent que genera contingut editorial.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, lectura_vigent_box,
                   minilectura, nom_ccaa_editorial,
                   source, page_meta, fnum, fpct, cagr, apply_layout,
                   load_geojson_spain_ccaa, canaries_inset_layers,
                   PURPLE, PURPLE_LIGHT, RED, GREEN, PALETTE)

inject_css()
t = setup_lang(show_selector=False)
page_header()
_ca = st.session_state.lang == "ca"


# ─── Càrrega de dades ──────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "empreses.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


df = load_data()


# ─── Classificació de règim (helper compartit) ─────────────────

def classificar_regim(acumulada_pct, anys_neg, anys_pos, yoy_pct, streak):
    """Classifica el règim actual del fenomen estructural d'empreses.

    Utilitzada per generar_subtitol_evolucio_empreses(). Mantinguda com a
    funció separada per a reutilització i claredat. La lògica equivalent
    també està inline a generar_lectura_vigent_empreses() pel pilot.
    """
    if yoy_pct > 0 and streak >= 3:
        return "recuperacio_consolidada" if acumulada_pct >= 0 else "inflexio"
    if acumulada_pct < -3 and abs(yoy_pct) < 0.5:
        return "estabilitzacio"
    if anys_neg > anys_pos and (anys_neg + anys_pos) >= 5:
        return "contraccio_estructural"
    if yoy_pct > 0 and streak < 3:
        return "creixement_puntual"
    return "altres"


# ─── Generació de la Lectura Vigent ────────────────────────────

def generar_lectura_vigent_empreses(df):
    """Genera dict {titol, data_referencia, autor} per la Lectura Vigent.

    Adaptativa a signe (caiguda/creixement), magnitud (suau/mig/forta) i racha
    (consecutivitat). Si la sèrie canvia de signe, la frase passa a una branca
    diferent sense contradicció. Sempre en castellà (coherent amb Tesi vigent).
    """
    autor = "Observatorio del Comercio · J3B3 Consulting"

    df_esp = df[df["territori"] == "espanya"].sort_values("any").copy()
    if len(df_esp) < 3:
        return {
            "titol": "Datos insuficientes para generar lectura vigente.",
            "data_referencia": "",
            "autor": autor,
        }

    last_year = int(df_esp.iloc[-1]["any"])
    last_emp = int(df_esp.iloc[-1]["empreses"])
    prev_emp = int(df_esp.iloc[-2]["empreses"])
    yoy_pct = (last_emp / prev_emp - 1) * 100
    yoy_abs = last_emp - prev_emp
    abs_yoy = abs(yoy_pct)

    # Racha: anys consecutius amb el mateix signe que yoy actual (mirant enrere)
    streak = 1
    for i in range(len(df_esp) - 2, 0, -1):
        prev_yoy = (df_esp.iloc[i]["empreses"] / df_esp.iloc[i - 1]["empreses"] - 1) * 100
        if (prev_yoy < 0) == (yoy_pct < 0):
            streak += 1
        else:
            break

    yoy_prev_pct = (prev_emp / int(df_esp.iloc[-3]["empreses"]) - 1) * 100

    if yoy_pct < 0:
        # CAIGUDA
        if abs_yoy < 0.5:
            titol = (
                f"Tras {streak} años de contracción, el número de empresas del "
                f"CNAE 47 se estabiliza en {last_year} con una caída interanual "
                f"contenida del {abs_yoy:.1f} %."
            )
        elif abs_yoy >= 3:
            titol = (
                f"El comercio minorista acelera la pérdida de tejido empresarial "
                f"en {last_year}: {fnum(abs(yoy_abs))} empresas menos en un año "
                f"({yoy_pct:+.1f} %)."
            )
        elif streak >= 10:
            titol = (
                f"El tejido empresarial del comercio minorista mantiene la "
                f"contracción una década después: {fnum(abs(yoy_abs))} empresas "
                f"menos en {last_year} ({yoy_pct:+.1f} %)."
            )
        elif streak >= 3:
            titol = (
                f"El tejido empresarial del comercio minorista mantiene la "
                f"contracción por {streak}º año consecutivo: "
                f"{fnum(abs(yoy_abs))} empresas menos en {last_year} "
                f"({yoy_pct:+.1f} %)."
            )
        else:
            titol = (
                f"El tejido empresarial del comercio minorista se reduce un "
                f"{abs_yoy:.1f} % en {last_year}, con {fnum(abs(yoy_abs))} "
                f"empresas menos que el año anterior."
            )
    else:
        # CREIXEMENT
        if abs_yoy < 0.5:
            titol = (
                f"El número de empresas del CNAE 47 se estabiliza en {last_year} "
                f"con una variación interanual mínima ({yoy_pct:+.1f} %)."
            )
        elif yoy_prev_pct < 0 and streak == 1:
            titol = (
                f"Primera señal de recuperación del tejido empresarial: el "
                f"CNAE 47 suma {fnum(yoy_abs)} empresas en {last_year} "
                f"({yoy_pct:+.1f} %)."
            )
        elif abs_yoy >= 3:
            titol = (
                f"El comercio minorista recupera dinamismo empresarial en "
                f"{last_year}: +{abs_yoy:.1f} % interanual, sumando "
                f"{fnum(yoy_abs)} empresas."
            )
        else:
            titol = (
                f"El tejido empresarial del comercio minorista crece un "
                f"{abs_yoy:.1f} % en {last_year}, sumando {fnum(yoy_abs)} "
                f"empresas."
            )

    return {
        "titol": titol,
        "data_referencia": f"Datos referidos a {last_year}",
        "autor": autor,
    }


# ─── Patró editorial Z · Nivell 2 (subtítols de gràfic) ────────

def generar_subtitol_evolucio_empreses(df):
    """Subtítol del gràfic d'evolució nacional, adaptatiu al règim actual.

    Reutilitza la lògica de classificar_regim() ja existent a través d'un
    recàlcul lleuger de les variables estructurals.
    """
    df_esp = (df[df["territori"] == "espanya"]
              .sort_values("any").reset_index(drop=True).copy())
    if len(df_esp) < 3:
        return "Evolución del tejido empresarial del CNAE 47"

    last_emp = int(df_esp.iloc[-1]["empreses"])
    prev_emp = int(df_esp.iloc[-2]["empreses"])
    yoy_pct = (last_emp / prev_emp - 1) * 100

    streak = 1
    for i in range(len(df_esp) - 2, 0, -1):
        prev_yoy = (df_esp.iloc[i]["empreses"]
                    / df_esp.iloc[i - 1]["empreses"] - 1) * 100
        if (prev_yoy < 0) == (yoy_pct < 0):
            streak += 1
        else:
            break

    df_esp["yoy_pct"] = df_esp["empreses"].pct_change() * 100
    pic_idx = df_esp["empreses"].idxmax()
    pic_any = int(df_esp.iloc[pic_idx]["any"])
    pic_emp = int(df_esp.iloc[pic_idx]["empreses"])
    acumulada_pct = (last_emp / pic_emp - 1) * 100
    acumulada_abs = last_emp - pic_emp
    post_pic = df_esp.iloc[pic_idx + 1:]
    anys_neg = int((post_pic["yoy_pct"] < 0).sum())
    anys_pos = int((post_pic["yoy_pct"] > 0).sum())

    regim = classificar_regim(acumulada_pct, anys_neg, anys_pos, yoy_pct, streak)

    if regim == "contraccio_estructural":
        return (f"Caída sostenida desde {pic_any}, con "
                f"{fnum(abs(acumulada_abs))} empresas menos acumuladas")
    elif regim == "inflexio":
        return (f"Recuperación incipiente tras {anys_neg} años de pérdidas "
                f"desde {pic_any}")
    elif regim == "estabilitzacio":
        return (f"Estabilización del tejido tras la contracción iniciada "
                f"en {pic_any}")
    elif regim == "recuperacio_consolidada":
        return f"Crecimiento sostenido del tejido empresarial desde {pic_any}"
    elif regim == "creixement_puntual":
        return (f"Repunte anual dentro de una trayectoria de caída desde "
                f"{pic_any}")
    return "Evolución del tejido empresarial del CNAE 47"


def generar_subtitol_mapa_empreses(mode, last_year):
    """Subtítol DESCRIPTIU del mapa, adaptatiu al mode (no interpretatiu).

    El mode és un selector de l'usuari; el subtítol confirma què està veient.
    La interpretació la fa la mini-lectura just sota.
    """
    if mode == "density":
        return (f"Densidad comercial por CCAA en {last_year} "
                f"(empresas por 1.000 habitantes)")
    return (f"Distribución del tejido empresarial por CCAA en {last_year} "
            f"(número de empresas)")


# ─── Patró editorial Z · Nivell 3 (mini-lectura del mapa) ──────

def generar_minilectura_mapa_empreses(df, mode, last_year):
    """Mini-lectura interpretativa del mapa, adaptativa al mode.

    Mode "absolute": top-3 i % concentració.
    Mode "density":
      - ratio < 1.3: homogeneïtat alta
      - ratio >= 1.3 + bottom_ccaa al top-3 absolut: frase de tensió
        (concentra molts pero registra densitat baixa)
      - ratio >= 1.3 + bottom_ccaa NO al top-3: fallback genèric
    """
    df_ccaa = df[df["territori"] != "espanya"]
    df_last = df_ccaa[df_ccaa["any"] == last_year]

    if mode == "absolute":
        df_sort = (df_last.sort_values("empreses", ascending=False)
                          .reset_index(drop=True))
        total = df_sort["empreses"].sum()
        top3 = [nom_ccaa_editorial(x)
                for x in df_sort.head(3)["territori"].tolist()]
        pct_top3 = df_sort.head(3)["empreses"].sum() / total * 100
        pct_s = f"{pct_top3:.1f}".replace(".", ",")
        if pct_top3 >= 50:
            return (f"{top3[0]}, {top3[1]} y {top3[2]} concentran el "
                    f"{pct_s} % del tejido empresarial del CNAE 47 en "
                    f"{last_year}, una concentración estructural elevada.")
        return (f"{top3[0]}, {top3[1]} y {top3[2]} concentran el {pct_s} % "
                f"del tejido empresarial del CNAE 47 en {last_year}, una "
                f"distribución consistente con el peso poblacional y "
                f"económico de las grandes áreas metropolitanas.")

    # Mode density
    df_d = (df_last.dropna(subset=["empreses_per_1000hab"])
                   .sort_values("empreses_per_1000hab", ascending=False)
                   .reset_index(drop=True))
    if df_d.empty:
        return ""

    top_raw = df_d.iloc[0]["territori"]
    bottom_raw = df_d.iloc[-1]["territori"]
    top_ccaa = nom_ccaa_editorial(top_raw)
    bottom_ccaa = nom_ccaa_editorial(bottom_raw)
    valor_top = df_d.iloc[0]["empreses_per_1000hab"]
    valor_bottom = df_d.iloc[-1]["empreses_per_1000hab"]
    ratio = valor_top / valor_bottom
    top_s = f"{valor_top:.1f}".replace(".", ",")
    bot_s = f"{valor_bottom:.1f}".replace(".", ",")
    ratio_s = f"{ratio:.1f}".replace(".", ",")

    if ratio < 1.3:
        return (f"En {last_year}, la densidad comercial es notablemente "
                f"homogénea entre CCAA: el rango va de {top_s} a {bot_s} "
                f"empresas/1.000 hab., un diferencial moderado.")

    # ratio >= 1.3: comprovar si bottom_raw és al top-3 absolut
    top3_abs_raw = (df_last.sort_values("empreses", ascending=False)
                           .head(3)["territori"].tolist())
    if bottom_raw in top3_abs_raw:
        return (f"En {last_year}, {bottom_ccaa} concentra el mayor número "
                f"de empresas pero registra la densidad comercial más baja "
                f"de España ({bot_s} empresas/1.000 hab.), frente a las "
                f"{top_s} de {top_ccaa}.")
    return (f"En {last_year}, la densidad comercial oscila entre {top_s} "
            f"empresas/1.000 hab. en {top_ccaa} y {bot_s} en {bottom_ccaa}, "
            f"con un diferencial de {ratio_s}× entre ambos extremos.")


# ─── Capçalera ─────────────────────────────────────────────────

st.title(t("emp_title"))
st.markdown(
    "*"
    + ("Evolució del teixit empresarial i densitat comercial a Espanya"
       if _ca else
       "Evolución del tejido empresarial y densidad comercial en España")
    + "*"
)

if df.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

# Separar CCAA del total nacional
ccaa_names = [t_name for t_name in df["territori"].unique() if t_name != "espanya"]
df_esp = df[df["territori"] == "espanya"].sort_values("any").copy()
df_ccaa = df[df["territori"].isin(ccaa_names)].copy()


# ─── Lectura Vigent ────────────────────────────────────────────

_lectura = generar_lectura_vigent_empreses(df)
lectura_vigent_box(
    titol=_lectura["titol"],
    data_referencia=_lectura["data_referencia"],
    autor=_lectura["autor"],
)


# ─── KPI únic gran amb delta interanual integrat ───────────────

if len(df_esp) >= 2:
    _last = df_esp.iloc[-1]
    _prev = df_esp.iloc[-2]
    _last_year = int(_last["any"])
    _prev_year = int(_prev["any"])
    _last_emp = int(_last["empreses"])
    _prev_emp = int(_prev["empreses"])
    _yoy_pct = (_last_emp / _prev_emp - 1) * 100
    _yoy_abs = _last_emp - _prev_emp

    # Color del delta segons signe i magnitud
    if abs(_yoy_pct) < 0.2:
        _delta_color = "#666"
        _arrow = "→"
    elif _yoy_pct < 0:
        _delta_color = "#c0392b"
        _arrow = "▼"
    else:
        _delta_color = "#27ae60"
        _arrow = "▲"

    _label = (f"Empreses CNAE 47 ({_last_year})" if _ca
              else f"Empresas CNAE 47 ({_last_year})")
    _delta_text = (
        f"{_arrow} {fnum(_yoy_abs)} empreses ({fpct(_yoy_pct, 1)}) vs {_prev_year}"
        if _ca else
        f"{_arrow} {fnum(_yoy_abs)} empresas ({fpct(_yoy_pct, 1)}) vs {_prev_year}"
    )

    st.markdown(
        f"""
        <div style="font-family:'DM Sans',sans-serif; margin:24px 0 28px;
                    padding:8px 0;">
            <div style="font-size:11px; color:#666; text-transform:uppercase;
                        letter-spacing:1.5px; font-weight:600;">
                {_label}
            </div>
            <div style="font-size:56px; font-weight:700; color:#0055a4;
                        line-height:1; margin-top:8px;">
                {fnum(_last_emp)}
            </div>
            <div style="font-size:13px; color:{_delta_color}; margin-top:8px;
                        font-weight:500;">
                {_delta_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Helper local: subtítol estilitzat sota un st.subheader ───

def _subtitol_grafic(text):
    """Subtítol descriptiu o interpretatiu sota el títol estable d'un gràfic.

    Estil: italica, color #666, font 13px, marge negatiu superior per pegar
    visualment al subheader, marge inferior 14px abans del gràfic.
    """
    st.markdown(
        f'<div style="color:#666; font-size:13px; font-style:italic; '
        f'font-family:\'DM Sans\',sans-serif; '
        f'margin:-12px 0 14px 4px;">{text}</div>',
        unsafe_allow_html=True,
    )


# ─── Gràfic nacional · Evolució empreses ───────────────────────

st.subheader("Empreses CNAE 47 · Espanya" if _ca else "Empresas CNAE 47 · España")
_subtitol_grafic(generar_subtitol_evolucio_empreses(df))

fig_evol = go.Figure()
fig_evol.add_trace(go.Scatter(
    x=df_esp["any"], y=df_esp["empreses"],
    mode="lines+markers", name=t("spain"),
    line=dict(color=PURPLE, width=2.5),
    marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(93,79,255,0.08)",
))
apply_layout(fig_evol, yaxis_title=t("emp_count"), height=400,
             yaxis_range=[350000, 600000])
st.plotly_chart(fig_evol, use_container_width=True)
source("INE, Directori Central d'Empreses (DIRCE)" if _ca
       else "INE, Directorio Central de Empresas (DIRCE)")


# ─── Mapa CCAA · Distribució territorial (amb toggle mètrica) ──

st.subheader("Distribució territorial · CCAA" if _ca
             else "Distribución territorial · CCAA")

if not df_ccaa.empty:
    _anys_ccaa = sorted(df_ccaa["any"].dropna().unique())

    _col_year, _col_metric = st.columns([1, 1])
    with _col_year:
        any_sel = st.select_slider(
            t("emp_ccaa_year"),
            options=_anys_ccaa,
            value=max(_anys_ccaa),
        )
    with _col_metric:
        _map_metric = st.radio(
            "Mètrica" if _ca else "Métrica",
            ["density", "absolute"],
            format_func=lambda x: (
                ("Empreses / 1.000 hab." if _ca else "Empresas / 1.000 hab.")
                if x == "density"
                else ("Empreses (absolut)" if _ca else "Empresas (absoluto)")
            ),
            horizontal=True,
            key="emp_map_metric",
        )

    # Subtítol descriptiu adaptatiu al mode (dins del bloc, post-selectors)
    _subtitol_grafic(generar_subtitol_mapa_empreses(_map_metric, int(any_sel)))

    df_map = df_ccaa[df_ccaa["any"] == any_sel].copy()

    @st.cache_data
    def _load_geojson():
        return load_geojson_spain_ccaa(with_canaries_inset=True)

    _geojson = _load_geojson()

    if _map_metric == "density" and "empreses_per_1000hab" in df_map.columns:
        _col_val = "empreses_per_1000hab"
        _lbl_legend = "Emp. / 1.000 hab."
        _fmt = ".1f"
        _zmin = df_ccaa["empreses_per_1000hab"].min()
        _zmax = df_ccaa["empreses_per_1000hab"].max()
    else:
        _col_val = "empreses"
        _lbl_legend = "Empreses" if _ca else "Empresas"
        _fmt = ",.0f"
        _zmin = df_ccaa["empreses"].min()
        _zmax = df_ccaa["empreses"].max()

    fig_map = go.Figure(go.Choroplethmap(
        geojson=_geojson,
        locations=df_map["territori"],
        featureidkey="properties.territori",
        z=df_map[_col_val],
        zmin=_zmin,
        zmax=_zmax,
        colorscale=[
            [0, "#e8f0fe"], [0.15, "#a8c8e8"], [0.35, "#5a9fd4"],
            [0.55, "#0055a4"], [0.75, "#003d7a"], [1, "#001d3d"],
        ],
        colorbar=dict(title=_lbl_legend, thickness=15),
        marker=dict(line=dict(width=1.5, color="white")),
        text=df_map["territori"],
        hovertemplate=(
            "<b>%{text}</b><br>"
            + f"{_lbl_legend}: " + "%{z:" + _fmt + "}<extra></extra>"
        ),
    ))
    fig_map.update_layout(
        map=dict(
            style="white-bg",
            center=dict(lat=38.7, lon=-4.0),
            zoom=4.55,
            layers=canaries_inset_layers(),
        ),
        height=700,
        margin=dict(l=0, r=0, t=10, b=10),
        dragmode=False,
        annotations=[dict(
            text="<b>CANÀRIES</b>" if _ca else "<b>CANARIAS</b>",
            xref="paper", yref="paper",
            x=0.18, y=0.18,
            showarrow=False,
            font=dict(size=10, color="#0055a4", family="DM Sans, sans-serif"),
        )],
    )
    st.plotly_chart(fig_map, use_container_width=True,
                    config={"scrollZoom": False, "doubleClick": False,
                            "displayModeBar": False})
    source("INE, DIRCE i Padrón Municipal. Càlcul propi" if _ca
           else "INE, DIRCE y Padrón Municipal. Cálculo propio")

    # Mini-lectura interpretativa, adaptativa al mode seleccionat
    minilectura(generar_minilectura_mapa_empreses(df, _map_metric, int(any_sel)))


# ─── Expander · Veure més detall ───────────────────────────────

with st.expander(("Veure més detall" if _ca else "Ver más detalle"),
                 expanded=False):

    # 1. Taxa variació anual nacional
    st.markdown("**" + ("Taxa variació anual (Espanya)" if _ca
                        else "Tasa variación anual (España)") + "**")

    if len(df_esp) > 1:
        df_esp = df_esp.copy()
        df_esp["var_pct"] = df_esp["empreses"].pct_change() * 100
        df_var = df_esp.dropna(subset=["var_pct"])
        _colors = [GREEN if v >= 0 else RED for v in df_var["var_pct"]]

        fig_var_nac = go.Figure()
        fig_var_nac.add_trace(go.Bar(
            x=df_var["any"], y=df_var["var_pct"],
            marker_color=_colors,
            text=[fpct(v) for v in df_var["var_pct"]],
            textposition="outside",
            textfont=dict(size=11),
        ))
        apply_layout(fig_var_nac,
                     yaxis_title=t("annual_variation") + " (%)",
                     height=380)
        fig_var_nac.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        st.plotly_chart(fig_var_nac, use_container_width=True)
        source("INE, DIRCE. Càlcul propi" if _ca else "INE, DIRCE. Cálculo propio")

    # 2. Rànquing CCAA — un sol gràfic amb toggle absolut/densitat
    if not df_ccaa.empty:
        st.markdown("---")
        st.markdown(
            "**"
            + (f"Rànquing per CCAA ({int(any_sel)})" if _ca
               else f"Ranking por CCAA ({int(any_sel)})")
            + "**"
        )

        _rank_metric = st.radio(
            "Mètrica del rànquing" if _ca else "Métrica del ranking",
            ["density", "absolute"],
            format_func=lambda x: (
                ("Empreses / 1.000 hab." if _ca else "Empresas / 1.000 hab.")
                if x == "density"
                else ("Empreses (absolut)" if _ca else "Empresas (absoluto)")
            ),
            horizontal=True,
            key="emp_rank_metric",
        )

        _df_rank = df_ccaa[df_ccaa["any"] == any_sel].copy()

        if _rank_metric == "density" and "empreses_per_1000hab" in _df_rank.columns:
            _df_rank = _df_rank.dropna(subset=["empreses_per_1000hab"])
            _df_rank = _df_rank.sort_values("empreses_per_1000hab", ascending=True)
            _x_col = "empreses_per_1000hab"
            _x_title = "Empreses / 1.000 hab." if _ca else "Empresas / 1.000 hab."
            _texts = [f"{v:.1f}".replace(".", ",") for v in _df_rank[_x_col]]
            _esp_ref_row = df_esp[df_esp["any"] == any_sel]
            _ref_col = "empreses_per_1000hab"
            _ref_lbl_es = "Espanya" if _ca else "España"
            _ref_fmt = lambda v: f"{v:.1f}".replace(".", ",")
        else:
            _df_rank = _df_rank.sort_values("empreses", ascending=True)
            _x_col = "empreses"
            _x_title = "Empreses" if _ca else "Empresas"
            _texts = [fnum(v) for v in _df_rank[_x_col]]
            _esp_ref_row = df_esp[df_esp["any"] == any_sel]
            _ref_col = "empreses"
            _ref_lbl_es = "Espanya" if _ca else "España"
            _ref_fmt = lambda v: fnum(v)

        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(
            y=_df_rank["territori"], x=_df_rank[_x_col],
            orientation="h",
            marker_color=PURPLE_LIGHT,
            text=_texts,
            textposition="outside",
            textfont=dict(size=11),
        ))
        if not _esp_ref_row.empty:
            _ref_val = _esp_ref_row.iloc[0][_ref_col]
            fig_rank.add_vline(
                x=_ref_val, line_dash="dash", line_color=RED, line_width=2,
                annotation_text=f"{_ref_lbl_es}: {_ref_fmt(_ref_val)}",
                annotation_position="top right",
            )
        apply_layout(fig_rank,
                     xaxis_title=_x_title,
                     height=max(450, len(_df_rank) * 30 + 80),
                     margin=dict(l=200, r=100, t=40, b=50))
        st.plotly_chart(fig_rank, use_container_width=True)
        source("INE, DIRCE i Padrón Municipal. Càlcul propi" if _ca
               else "INE, DIRCE y Padrón Municipal. Cálculo propio")

    # 3. Variació acumulada per CCAA
    if not df_ccaa.empty:
        st.markdown("---")
        _first_year = df_ccaa["any"].min()
        _last_year_ccaa = df_ccaa["any"].max()
        st.markdown(
            "**"
            + (f"Variació acumulada {int(_first_year)}-{int(_last_year_ccaa)} per CCAA"
               if _ca else
               f"Variación acumulada {int(_first_year)}-{int(_last_year_ccaa)} por CCAA")
            + "**"
        )

        df_first = df_ccaa[df_ccaa["any"] == _first_year][["territori", "empreses"]] \
            .rename(columns={"empreses": "emp_first"})
        df_last = df_ccaa[df_ccaa["any"] == _last_year_ccaa][["territori", "empreses"]] \
            .rename(columns={"empreses": "emp_last"})
        df_var_ccaa = df_first.merge(df_last, on="territori")
        df_var_ccaa["var_pct"] = (
            (df_var_ccaa["emp_last"] / df_var_ccaa["emp_first"]) - 1
        ) * 100
        df_var_ccaa = df_var_ccaa.sort_values("var_pct", ascending=True)

        fig_var_ccaa = go.Figure()
        _colors_var = [GREEN if v >= 0 else RED for v in df_var_ccaa["var_pct"]]
        fig_var_ccaa.add_trace(go.Bar(
            y=df_var_ccaa["territori"], x=df_var_ccaa["var_pct"],
            orientation="h",
            marker_color=_colors_var,
            text=[fpct(v) for v in df_var_ccaa["var_pct"]],
            textposition="outside",
            textfont=dict(size=11),
        ))
        apply_layout(fig_var_ccaa,
                     xaxis_title=("Variació acumulada (%)" if _ca
                                  else "Variación acumulada (%)"),
                     height=max(450, len(df_var_ccaa) * 30 + 80),
                     margin=dict(l=200, r=80, t=30, b=50))
        fig_var_ccaa.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        st.plotly_chart(fig_var_ccaa, use_container_width=True)
        source("INE, DIRCE. Càlcul propi" if _ca
               else "INE, DIRCE. Cálculo propio")

    # 4. Evolució CCAA seleccionades amb multiselect
    if not df_ccaa.empty:
        st.markdown("---")
        st.markdown("**" + t("emp_ccaa_evolution") + "**")

        _default_ccaa = [c for c in ["Cataluña", "Madrid (Comunidad de)", "Andalucía",
                                     "Comunitat Valenciana"] if c in ccaa_names]
        sel_ccaa = st.multiselect(t("emp_ccaa_select"),
                                  sorted(ccaa_names),
                                  default=_default_ccaa)

        if sel_ccaa:
            fig_evol_ccaa = go.Figure()
            for i, _ccaa in enumerate(sel_ccaa):
                _df_c = df_ccaa[df_ccaa["territori"] == _ccaa].sort_values("any")
                fig_evol_ccaa.add_trace(go.Scatter(
                    x=_df_c["any"], y=_df_c["empreses"],
                    mode="lines+markers", name=_ccaa,
                    line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                    marker=dict(size=5),
                ))
            apply_layout(fig_evol_ccaa, yaxis_title=t("emp_count"), height=420)
            st.plotly_chart(fig_evol_ccaa, use_container_width=True)
            source("INE, DIRCE")


# ─── Expander · Metodologia i fonts ────────────────────────────

with st.expander(("Metodologia i fonts" if _ca else "Metodología y fuentes"),
                 expanded=False):
    if _ca:
        st.markdown(
            """
**Què mesurem.** El nombre d'**empreses actives** del comerç al detall
(CNAE 47) reflecteix la salut i la dinàmica del teixit empresarial del
sector. Una caiguda sostinguda no sempre és negativa: pot indicar
**concentració** (menys empreses, però més grans i eficients) o bé
**destrucció neta** per pressió competitiva i digitalització. La
comparativa per comunitats autònomes permet identificar quins territoris
perden o guanyen pes relatiu en el comerç al detall.

**Fonts utilitzades.**
- **INE — Directori Central d'Empreses (DIRCE)**: nombre d'empreses
  actives. Combinació de taules 39372 (CCAA + Nacional, 2020 endavant),
  3954 (Nacional, des de 2013) i 298 (CCAA + Nacional, històrica
  2008-2020) per a la sèrie més llarga possible sense duplicacions.
- **INE — Padrón Municipal** (taules 2915 i 56934) i estimació proporcional
  per a 2022-2025: població base per al càlcul de densitat
  (empreses / 1.000 habitants).

**Notes interpretatives.**
- La densitat comercial cau pel doble efecte de menys empreses i més
  població.
- Entre 2022 i 2023 algunes CCAA mostren un salt metodològic notable per
  l'actualització del DIRCE; no és necessàriament destrucció real.
- Vegeu l'apartat 5 de **Metodologia** per al detall de fonts i
  combinacions de taules.
            """
        )
    else:
        st.markdown(
            """
**Qué medimos.** El número de **empresas activas** del comercio
minorista (CNAE 47) refleja la salud y la dinámica del tejido
empresarial del sector. Una caída sostenida no siempre es negativa:
puede indicar **concentración** (menos empresas, pero más grandes y
eficientes) o bien **destrucción neta** por presión competitiva y
digitalización. La comparativa por comunidades autónomas permite
identificar qué territorios pierden o ganan peso relativo en el comercio
minorista.

**Fuentes utilizadas.**
- **INE — Directorio Central de Empresas (DIRCE)**: número de empresas
  activas. Combinación de tablas 39372 (CCAA + Nacional, 2020 en
  adelante), 3954 (Nacional, desde 2013) y 298 (CCAA + Nacional,
  histórica 2008-2020) para la serie más larga posible sin duplicaciones.
- **INE — Padrón Municipal** (tablas 2915 y 56934) y estimación
  proporcional para 2022-2025: población base para el cálculo de
  densidad (empresas / 1.000 habitantes).

**Notas interpretativas.**
- La densidad comercial cae por el doble efecto de menos empresas y más
  población.
- Entre 2022 y 2023 algunas CCAA muestran un salto metodológico notable
  por la actualización del DIRCE; no es necesariamente destrucción real.
- Véase el apartado 5 de **Metodología** para el detalle de fuentes y
  combinaciones de tablas.
            """
        )


# ─── Peu · descàrrega CSV ──────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"),
                       "empreses_cnae47.csv", "text/csv")


page_meta("INE, Directori Central d'Empreses (DIRCE)" if _ca
          else "INE, Directorio Central de Empresas (DIRCE)",
          st.session_state.lang)
