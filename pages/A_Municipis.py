"""Pagina A: Mapa municipal - index de capacitat comercial per municipi."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, page_header, insight, intro, source, page_meta,
                   fnum, fpct, apply_layout,
                   PURPLE, PURPLE_LIGHT, RED, GREEN, ORANGE, PALETTE)

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"

@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "municipal.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

st.title("Capacitat comercial municipal" if _ca else "Capacidad comercial municipal")

if _ca:
    intro(
        "Aquesta secció presenta un <strong>índex de capacitat comercial</strong> per als municipis "
        "espanyols (només els de més de 5.000 habitants). L'índex combina, en escala 0-100: el "
        "<strong>nombre absolut</strong> d'empreses del sector comerç-transport-hostaleria del municipi "
        "(escala logarítmica) i la <strong>densitat empresarial</strong> per cada 1.000 habitants. "
        "<br><br>"
        "<strong>Avís metodològic important.</strong> L'INE no publica el detall del CNAE 47 (comerç al "
        "detall) a nivell municipal — només el sector agregat <em>G-I</em> que inclou comerç al detall, "
        "comerç majorista, reparació de vehicles, transport i hostaleria. Aquest índex, per tant, "
        "<strong>no és VAB CNAE 47 estricte</strong>: és una proxy comparativa del teixit comercial+serveis "
        "associats per municipi. Municipis turístics tindran l'índex inflat per la presència d'hostaleria; "
        "municipis amb gran activitat logística també. La metodologia detallada és a la pàgina Metodologia."
    )
else:
    intro(
        "Esta sección presenta un <strong>índice de capacidad comercial</strong> para los municipios "
        "españoles (solo los de más de 5.000 habitantes). El índice combina, en escala 0-100: el "
        "<strong>número absoluto</strong> de empresas del sector comercio-transporte-hostelería del "
        "municipio (escala logarítmica) y la <strong>densidad empresarial</strong> por cada 1.000 "
        "habitantes. "
        "<br><br>"
        "<strong>Aviso metodológico importante.</strong> El INE no publica el detalle del CNAE 47 "
        "(comercio minorista) a nivel municipal — solo el sector agregado <em>G-I</em> que incluye "
        "comercio minorista, comercio mayorista, reparación de vehículos, transporte y hostelería. "
        "Este índice, por tanto, <strong>no es VAB CNAE 47 estricto</strong>: es una proxy comparativa "
        "del tejido comercio+servicios asociados por municipio. Municipios turísticos tendrán el índice "
        "inflado por la presencia de hostelería; municipios con gran actividad logística también."
    )

if df.empty or "index_capacitat" not in df.columns:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

df_idx = df.dropna(subset=["index_capacitat"]).copy()

# ─── KPIs superiors ──────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Municipis analitzats" if _ca else "Municipios analizados",
    fnum(len(df_idx)),
    help=("Municipis amb >5.000 habitants i dades completes" if _ca
          else "Municipios con >5.000 habitantes y datos completos"),
)
top_mun = df_idx.iloc[df_idx["index_capacitat"].idxmax()]
col2.metric(
    "Líder" if _ca else "Líder",
    str(top_mun["municipi"]),
    delta=f"{top_mun['index_capacitat']:.1f}".replace(".", ",") + " idx",
    delta_color="off",
)
total_emp_gi = df_idx["empreses_g_i"].sum()
col3.metric(
    "Empreses G-I total" if _ca else "Empresas G-I total",
    fnum(total_emp_gi),
)
densitat_mitjana = df_idx["gi_per_1000hab"].median()
col4.metric(
    "Densitat mitjana" if _ca else "Densidad mediana",
    f"{densitat_mitjana:.1f}".replace(".", ","),
    help=("Empreses G-I per 1.000 hab. (mediana del conjunt)" if _ca
          else "Empresas G-I por 1.000 hab. (mediana del conjunto)"),
)

st.markdown("---")

# ─── Selector ────────────────────────────────────────────────

st.subheader("Rànquing de municipis" if _ca else "Ranking de municipios")

n_top = st.select_slider(
    ("Mostrar Top N" if _ca else "Mostrar Top N"),
    options=[10, 25, 50, 100, 250, 500],
    value=25,
)

ordenar_per = st.radio(
    ("Ordenar per" if _ca else "Ordenar por"),
    options=["index_capacitat", "empreses_g_i", "gi_per_1000hab"],
    format_func=lambda c: {
        "index_capacitat": "Índex de capacitat" if _ca else "Índice de capacidad",
        "empreses_g_i": "Empreses absolutes" if _ca else "Empresas absolutas",
        "gi_per_1000hab": "Densitat (per 1.000 hab.)" if _ca else "Densidad (por 1.000 hab.)",
    }.get(c, c),
    horizontal=True,
)

df_sorted = df_idx.sort_values(ordenar_per, ascending=False).head(n_top)

# ─── Gràfic horitzontal ─────────────────────────────────────

fig = go.Figure()
fig.add_trace(go.Bar(
    y=df_sorted["municipi"][::-1],
    x=df_sorted[ordenar_per][::-1],
    orientation="h",
    marker_color=PURPLE,
    text=[f"{v:.1f}".replace(".", ",") if ordenar_per != "empreses_g_i" else fnum(v)
          for v in df_sorted[ordenar_per][::-1]],
    textposition="outside",
    textfont=dict(size=10),
    customdata=df_sorted[["empreses_g_i", "poblacio", "gi_per_1000hab", "index_capacitat"]][::-1].values,
    hovertemplate=(
        "<b>%{y}</b><br>"
        + ("Empreses G-I: " if _ca else "Empresas G-I: ") + "%{customdata[0]:,.0f}<br>"
        + ("Població: " if _ca else "Población: ") + "%{customdata[1]:,.0f}<br>"
        + ("Densitat: " if _ca else "Densidad: ") + "%{customdata[2]:.1f}<br>"
        + ("Índex: " if _ca else "Índice: ") + "%{customdata[3]:.1f}<extra></extra>"
    ).replace(",", "."),
))

xaxis_title = {
    "index_capacitat": ("Índex (0-100)" if _ca else "Índice (0-100)"),
    "empreses_g_i": ("Empreses G-I" if _ca else "Empresas G-I"),
    "gi_per_1000hab": ("Empreses G-I per 1.000 hab." if _ca else "Empresas G-I por 1.000 hab."),
}[ordenar_per]

apply_layout(fig,
    xaxis_title=xaxis_title,
    height=max(400, n_top * 22 + 100),
    margin=dict(l=200, r=80, t=20, b=40),
    hovermode="closest",
)
st.plotly_chart(fig, use_container_width=True)
source("INE, Directori Central d'Empreses (T=4721) i Padró Municipal (T=33167). Càlcul propi"
       if _ca else
       "INE, Directorio Central de Empresas (T=4721) y Padrón Municipal (T=33167). Cálculo propio")

# ─── Scatter empreses vs població ───────────────────────────

st.subheader("Relació empreses ↔ població" if _ca else "Relación empresas ↔ población")

fig_sc = go.Figure()
fig_sc.add_trace(go.Scatter(
    x=df_idx["poblacio"],
    y=df_idx["empreses_g_i"],
    mode="markers",
    marker=dict(
        size=df_idx["index_capacitat"] / 4 + 4,
        color=df_idx["gi_per_1000hab"],
        colorscale=[[0, "#e8f0fe"], [0.5, "#5a9fd4"], [1, "#0055a4"]],
        showscale=True,
        colorbar=dict(title=("Densitat" if _ca else "Densidad"), thickness=15),
        line=dict(width=0.5, color="white"),
    ),
    text=df_idx["municipi"],
    customdata=df_idx[["empreses_g_i", "poblacio", "gi_per_1000hab", "index_capacitat"]].values,
    hovertemplate=(
        "<b>%{text}</b><br>"
        + ("Pob.: " if _ca else "Pob.: ") + "%{customdata[1]:,.0f}<br>"
        + ("Empr. G-I: " if _ca else "Empr. G-I: ") + "%{customdata[0]:,.0f}<br>"
        + ("Densitat: " if _ca else "Densidad: ") + "%{customdata[2]:.1f}<br>"
        + ("Índex: " if _ca else "Índice: ") + "%{customdata[3]:.1f}<extra></extra>"
    ).replace(",", "."),
))

apply_layout(fig_sc,
    xaxis_title=("Població" if _ca else "Población") + " (escala logarítmica)",
    yaxis_title=("Empreses G-I" if _ca else "Empresas G-I") + " (escala logarítmica)",
    height=520,
    hovermode="closest",
)
fig_sc.update_xaxes(type="log")
fig_sc.update_yaxes(type="log")
st.plotly_chart(fig_sc, use_container_width=True)
source("INE, Directori Central d'Empreses i Padró Municipal. Càlcul propi"
       if _ca else
       "INE, Directorio Central de Empresas y Padrón Municipal. Cálculo propio")

if _ca:
    insight(
        f"<strong>Lectura del gràfic.</strong> "
        f"La línia diagonal implícita reflecteix una relació proporcional entre població i empreses "
        f"comercials. Els municipis <strong>per sobre de la diagonal</strong> tenen més empreses G-I "
        f"del que correspondria a la seva població (potencial sobreoferta o municipis amb activitat "
        f"comercial atípica — turisme, logística). Els <strong>per sota</strong>, menys empreses del "
        f"que correspondria (potencial dèficit comercial, dependència de municipis veïns)."
        f"<br><br>"
        f"<strong>Limitacions de l'índex.</strong> El sector G-I de l'INE inclou no només el comerç "
        f"al detall sinó també hostaleria, transport i comerç majorista. Per això municipis com "
        f"<strong>Cangas de Onís, Marbella o Benidorm</strong> tenen un índex alt: el seu sector G-I "
        f"està dominat per <em>hostaleria turística</em>, no pel comerç al detall pròpiament dit. "
        f"En canvi, ciutats com Madrid o Barcelona apareixen amb una densitat per habitant moderada "
        f"perquè diluint el comerç sobre una població molt alta dóna ràtios baixos."
    )
else:
    insight(
        f"<strong>Lectura del gráfico.</strong> "
        f"La línea diagonal implícita refleja una relación proporcional entre población y empresas "
        f"comerciales. Los municipios <strong>por encima de la diagonal</strong> tienen más empresas "
        f"G-I de lo que correspondería a su población (potencial sobreoferta o municipios con "
        f"actividad comercial atípica — turismo, logística). Los <strong>por debajo</strong>, menos "
        f"empresas de lo que correspondería (potencial déficit comercial, dependencia de municipios "
        f"vecinos)."
        f"<br><br>"
        f"<strong>Limitaciones del índice.</strong> El sector G-I del INE incluye no solo el comercio "
        f"minorista sino también hostelería, transporte y comercio mayorista. Por eso municipios "
        f"como <strong>Cangas de Onís, Marbella o Benidorm</strong> tienen un índice alto: su sector "
        f"G-I está dominado por <em>hostelería turística</em>, no por el comercio minorista. En "
        f"cambio, ciudades como Madrid o Barcelona aparecen con una densidad por habitante moderada "
        f"porque diluir el comercio sobre una población muy alta da ratios bajos."
    )

# ─── Descàrrega ──────────────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df_idx.sort_values("index_capacitat", ascending=False), use_container_width=True, hide_index=True)
    st.download_button(
        "CSV",
        df_idx.to_csv(index=False).encode("utf-8"),
        "capacitat_comercial_municipal.csv",
        "text/csv",
    )

page_meta(
    "INE: DIRCE T=4721 i Padró T=33167. Càlcul propi" if _ca
    else "INE: DIRCE T=4721 y Padrón T=33167. Cálculo propio",
    st.session_state.lang,
)
