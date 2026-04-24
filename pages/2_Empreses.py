"""Pàgina 2: Teixit Empresarial (CNAE 47)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import (inject_css, setup_lang, insight, intro, source, page_meta,
                   fnum, fpct, cagr, apply_layout,
                   PURPLE, PURPLE_LIGHT, RED, GREEN, PALETTE)

inject_css()
t = setup_lang(show_selector=False)

@st.cache_data(ttl=3600)
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "empreses.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

st.title(t("emp_title"))

if st.session_state.lang == "ca":
    intro(
        "El nombre d'<strong>empreses actives</strong> del comerç al detall (CNAE 47) reflecteix "
        "la salut i la dinàmica del teixit empresarial del sector. Una caiguda sostinguda no sempre "
        "és negativa: pot indicar <strong>concentració</strong> (menys empreses, però més grans i eficients) "
        "o bé <strong>destrucció neta</strong> per pressió competitiva i digitalització. "
        "La comparativa per comunitats autònomes permet identificar quins territoris perden o guanyen "
        "pes relatiu en el comerç al detall."
    )
else:
    intro(
        "El número de <strong>empresas activas</strong> del comercio minorista (CNAE 47) refleja "
        "la salud y la dinámica del tejido empresarial del sector. Una caída sostenida no siempre "
        "es negativa: puede indicar <strong>concentración</strong> (menos empresas, pero más grandes y eficientes) "
        "o bien <strong>destrucción neta</strong> por presión competitiva y digitalización. "
        "La comparativa por comunidades autónomas permite identificar qué territorios pierden o ganan "
        "peso relativo en el comercio minorista."
    )

if df.empty:
    st.warning("No hi ha dades disponibles." if st.session_state.lang == "ca"
               else "No hay datos disponibles.")
    st.stop()

# Separar CCAA del total nacional
ccaa_names = [t_name for t_name in df["territori"].unique() if t_name != "espanya"]
df_esp = df[df["territori"] == "espanya"].sort_values("any").copy()
df_ccaa = df[df["territori"].isin(ccaa_names)].copy()

_ca = st.session_state.lang == "ca"

# ─── KPIs superiors ──────────────────────────────────────────

if not df_esp.empty and len(df_esp) > 1:
    first_esp = df_esp.iloc[0]
    last_esp = df_esp.iloc[-1]
    total_var = int(last_esp["empreses"]) - int(first_esp["empreses"])
    pct_var = (total_var / int(first_esp["empreses"])) * 100
    cagr_val = cagr(first_esp["empreses"], last_esp["empreses"],
                    int(last_esp["any"]) - int(first_esp["any"]))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"{'Empreses' if _ca else 'Empresas'} ({int(last_esp['any'])})", fnum(last_esp['empreses']))
    col2.metric(f"{'Variació' if _ca else 'Variación'} {int(first_esp['any'])}-{int(last_esp['any'])}", fpct(pct_var))
    col3.metric("Empreses perdudes" if _ca else "Empresas perdidas", fnum(total_var))
    col4.metric("CAGR", fpct(cagr_val, 2))

# ─── Gràfic 1: Evolució Espanya ──────────────────────────────

st.subheader(t("emp_evolution"))

fig = go.Figure()
if not df_esp.empty:
    fig.add_trace(go.Scatter(
        x=df_esp["any"], y=df_esp["empreses"],
        mode="lines+markers", name=t("spain"),
        line=dict(color=PURPLE, width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(93,79,255,0.08)",
    ))

apply_layout(fig, yaxis_title=t("emp_count"), height=400, yaxis_range=[350000, 600000])
st.plotly_chart(fig, use_container_width=True)
source("INE, Directori Central d'Empreses (DIRCE)" if _ca
       else "INE, Directorio Central de Empresas (DIRCE)")

# ─── Gràfic 2: Taxa variació anual ──────────────────────────

st.subheader(t("emp_destruction"))

if len(df_esp) > 1:
    df_esp["var_pct"] = df_esp["empreses"].pct_change() * 100

    fig2 = go.Figure()
    df_var = df_esp.dropna(subset=["var_pct"])
    colors = [GREEN if v >= 0 else RED for v in df_var["var_pct"]]

    fig2.add_trace(go.Bar(
        x=df_var["any"], y=df_var["var_pct"],
        marker_color=colors,
        text=[fpct(v) for v in df_var["var_pct"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig2, yaxis_title=t("annual_variation") + " (%)", height=400)
    fig2.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    st.plotly_chart(fig2, use_container_width=True)
    source("INE, DIRCE. Càlcul propi" if _ca else "INE, DIRCE. Cálculo propio")

# ─── Insight Empreses ────────────────────────────────────────

if not df_esp.empty and len(df_esp) > 1:
    peak = df_esp.loc[df_esp["empreses"].idxmax()]
    if _ca:
        txt = (
            f"El comerç al detall espanyol comptava amb <strong>{fnum(last_esp['empreses'])} empreses</strong> "
            f"el {int(last_esp['any'])}, <strong>{fnum(abs(total_var))} menys</strong> que el {int(first_esp['any'])} "
            f"({fpct(pct_var)}). "
            f"El màxim es va registrar el {int(peak['any'])} amb {fnum(peak['empreses'])} empreses. "
            f"Això suposa una destrucció neta anual mitjana (CAGR) del <strong>{fpct(cagr_val, 2)}</strong>. "
            f"La tendència reflecteix la concentració del sector i la pressió del comerç electrònic. "
            f"Malgrat la reducció del nombre d'empreses, la dimensió mitjana creix: les empreses "
            f"supervivents absorbeixen quota de mercat i guanyen escala operativa."
        )
    else:
        txt = (
            f"El comercio minorista español contaba con <strong>{fnum(last_esp['empreses'])} empresas</strong> "
            f"en {int(last_esp['any'])}, <strong>{fnum(abs(total_var))} menos</strong> que en {int(first_esp['any'])} "
            f"({fpct(pct_var)}). "
            f"El máximo se registró en {int(peak['any'])} con {fnum(peak['empreses'])} empresas. "
            f"Esto supone una destrucción neta anual media (CAGR) del <strong>{fpct(cagr_val, 2)}</strong>. "
            f"La tendencia refleja la concentración del sector y la presión del comercio electrónico. "
            f"Pese a la reducción del número de empresas, la dimensión media crece: las empresas "
            f"supervivientes absorben cuota de mercado y ganan escala operativa."
        )
    insight(txt)

# ─── Densitat comercial: empreses / 1.000 habitants ──────────

if "empreses_per_1000hab" in df_esp.columns:
    st.subheader("Densitat comercial (empreses per 1.000 habitants)" if _ca
                 else "Densidad comercial (empresas por 1.000 habitantes)")

    df_dens = df_esp.dropna(subset=["empreses_per_1000hab"])
    fig_dens = go.Figure()
    fig_dens.add_trace(go.Scatter(
        x=df_dens["any"], y=df_dens["empreses_per_1000hab"],
        mode="lines+markers",
        line=dict(color=PURPLE, width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(93,79,255,0.08)",
        text=[f"{v:.2f}".replace(".", ",") for v in df_dens["empreses_per_1000hab"]],
        hovertemplate="%{x}: %{text} emp/1.000 hab<extra></extra>",
    ))
    apply_layout(fig_dens,
        yaxis_title=("Empreses / 1.000 hab." if _ca else "Empresas / 1.000 hab."),
        height=400,
    )
    st.plotly_chart(fig_dens, use_container_width=True)
    source("INE, DIRCE i Padrón Municipal. Càlcul propi" if _ca
           else "INE, DIRCE y Padrón Municipal. Cálculo propio")

    if len(df_dens) > 1:
        d_first = df_dens.iloc[0]["empreses_per_1000hab"]
        d_last = df_dens.iloc[-1]["empreses_per_1000hab"]
        var_dens = ((d_last / d_first) - 1) * 100
        if _ca:
            insight(
                f"La densitat comercial ha passat de <strong>{fnum(d_first, 2)} empreses per 1.000 habitants</strong> "
                f"({int(df_dens.iloc[0]['any'])}) a <strong>{fnum(d_last, 2)}</strong> ({int(df_dens.iloc[-1]['any'])}), "
                f"una caiguda del <strong>{fpct(abs(var_dens), 1, sign=False)}</strong>. "
                f"Això reflecteix un doble efecte: la destrucció d'empreses i el creixement de la població, "
                f"que junts redueixen la proximitat del comerç al ciutadà. "
                f"La pèrdua de densitat comercial impacta especialment en àrees rurals i barris perifèrics, "
                f"on el comerç de proximitat té un paper social més enllà del purament econòmic."
            )
        else:
            insight(
                f"La densidad comercial ha pasado de <strong>{fnum(d_first, 2)} empresas por 1.000 habitantes</strong> "
                f"({int(df_dens.iloc[0]['any'])}) a <strong>{fnum(d_last, 2)}</strong> ({int(df_dens.iloc[-1]['any'])}), "
                f"una caída del <strong>{fpct(abs(var_dens), 1, sign=False)}</strong>. "
                f"Esto refleja un doble efecto: la destrucción de empresas y el crecimiento de la población, "
                f"que juntos reducen la proximidad del comercio al ciudadano. "
                f"La pérdida de densidad comercial impacta especialmente en áreas rurales y barrios periféricos, "
                f"donde el comercio de proximidad tiene un papel social más allá de lo puramente económico."
            )

# ─── Mapa interactiu CCAA ────────────��───────────────────────

st.markdown("---")
st.subheader(t("emp_ccaa_title"))

if not df_ccaa.empty:
    import json

    @st.cache_data
    def load_geojson():
        path = os.path.join(os.path.dirname(__file__), "..", "data", "geo", "spain_ccaa.geojson")
        with open(path, "r") as f:
            return json.load(f)

    geojson = load_geojson()

    any_sel = st.select_slider(
        t("emp_ccaa_year"),
        options=sorted(df_ccaa["any"].dropna().unique()),
        value=max(df_ccaa["any"].dropna().unique()),
    )

    df_map = df_ccaa[df_ccaa["any"] == any_sel].copy()

    tab_map, tab_rank = st.tabs([
        "Mapa" if _ca else "Mapa",
        "Rànquing" if _ca else "Ranking",
    ])

    with tab_map:
        map_metric = st.radio(
            "Mètrica" if _ca else "Métrica",
            ["density", "absolute"],
            format_func=lambda x: (
                ("Empreses / 1.000 hab." if _ca else "Empresas / 1.000 hab.") if x == "density"
                else ("Empreses (absolut)" if _ca else "Empresas (absoluto)")
            ),
            horizontal=True,
        )

        if map_metric == "density" and "empreses_per_1000hab" in df_map.columns:
            col_val = "empreses_per_1000hab"
            lbl_legend = "Emp. / 1.000 hab." if _ca else "Emp. / 1.000 hab."
            fmt = ".1f"
            zmin = df_ccaa["empreses_per_1000hab"].min()
            zmax = df_ccaa["empreses_per_1000hab"].max()
        else:
            col_val = "empreses"
            lbl_legend = "Empreses" if _ca else "Empresas"
            fmt = ",.0f"
            zmin = df_ccaa["empreses"].min()
            zmax = df_ccaa["empreses"].max()

        fig_map = go.Figure(go.Choroplethmap(
            geojson=geojson,
            locations=df_map["territori"],
            featureidkey="properties.territori",
            z=df_map[col_val],
            zmin=zmin,
            zmax=zmax,
            colorscale=[
                [0, "#f0eeff"],
                [0.15, "#c4b5fd"],
                [0.35, "#8b5cf6"],
                [0.55, "#6d28d9"],
                [0.75, "#4c1d95"],
                [1, "#1e0a3c"],
            ],
            colorbar=dict(title=lbl_legend, thickness=15),
            marker=dict(line=dict(width=1.5, color="white")),
            text=df_map["territori"],
            hovertemplate=(
                "<b>%{text}</b><br>" +
                f"{lbl_legend}: " + "%{z:" + fmt + "}<extra></extra>"
            ),
        ))
        fig_map.update_layout(
            map=dict(
                style="white-bg",
                center=dict(lat=39.5, lon=-3.5),
                zoom=4.8,
            ),
            height=800,
            margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        source("INE, DIRCE i Padrón Municipal. Càlcul propi" if _ca
               else "INE, DIRCE y Padrón Municipal. Cálculo propio")

    with tab_rank:
        # Rànquing horitzontal per empreses
        df_any = df_ccaa[df_ccaa["any"] == any_sel].sort_values("empreses", ascending=True)

        total_esp_val = df_esp[df_esp["any"] == any_sel]["empreses"].values
        total_val = total_esp_val[0] if len(total_esp_val) > 0 else df_any["empreses"].sum()

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            y=df_any["territori"], x=df_any["empreses"],
            orientation="h",
            marker_color=PURPLE_LIGHT,
            text=[f"{fnum(v)}  ({fpct(v / total_val * 100, 1, sign=False)})" for v in df_any["empreses"]],
            textposition="outside",
            textfont=dict(size=11),
        ))
        n_ccaa = len(df_any)
        if n_ccaa > 0:
            avg_emp = total_val / n_ccaa
            fig3.add_vline(
                x=avg_emp, line_dash="dash", line_color=RED, line_width=2,
                annotation_text=f"{'Mitjana' if _ca else 'Media'}: {fnum(avg_emp)}",
                annotation_position="top right",
            )
        apply_layout(fig3,
            title=f"{t('emp_ccaa_ranking')} ({int(any_sel)})",
            xaxis_title=t("emp_count"),
            height=max(450, len(df_any) * 32 + 100),
            margin=dict(l=200, r=120, t=50, b=50),
        )
        st.plotly_chart(fig3, use_container_width=True)
        source("INE, DIRCE")

        # Rànquing densitat comercial per CCAA
        if "empreses_per_1000hab" in df_ccaa.columns:
            df_dens_ccaa = df_ccaa[df_ccaa["any"] == any_sel].dropna(subset=["empreses_per_1000hab"])
            if not df_dens_ccaa.empty:
                lbl_dens = ("Densitat comercial per CCAA (empreses / 1.000 hab.)" if _ca
                            else "Densidad comercial por CCAA (empresas / 1.000 hab.)")
                st.subheader(f"{lbl_dens} ({int(any_sel)})")

                df_dens_ccaa = df_dens_ccaa.sort_values("empreses_per_1000hab", ascending=True)

                esp_dens = df_esp[df_esp["any"] == any_sel]["empreses_per_1000hab"].values
                avg_dens = esp_dens[0] if len(esp_dens) > 0 else None

                fig_dens_ccaa = go.Figure()
                fig_dens_ccaa.add_trace(go.Bar(
                    y=df_dens_ccaa["territori"], x=df_dens_ccaa["empreses_per_1000hab"],
                    orientation="h",
                    marker_color=PURPLE_LIGHT,
                    text=[f"{v:.1f}".replace(".", ",") for v in df_dens_ccaa["empreses_per_1000hab"]],
                    textposition="outside",
                    textfont=dict(size=11),
                ))
                if avg_dens:
                    fig_dens_ccaa.add_vline(
                        x=avg_dens, line_dash="dash", line_color=RED, line_width=2,
                        annotation_text=f"{'Espanya' if _ca else 'España'}: {avg_dens:.1f}".replace(".", ","),
                        annotation_position="top right",
                    )
                apply_layout(fig_dens_ccaa,
                    xaxis_title=("Empreses / 1.000 hab." if _ca else "Empresas / 1.000 hab."),
                    height=max(450, len(df_dens_ccaa) * 32 + 100),
                    margin=dict(l=200, r=100, t=50, b=50),
                )
                st.plotly_chart(fig_dens_ccaa, use_container_width=True)
                source("INE, DIRCE i Padrón Municipal. Càlcul propi" if _ca
                       else "INE, DIRCE y Padrón Municipal. Cálculo propio")

    # Variació acumulada per CCAA (fora dels tabs)
    first_year = df_ccaa["any"].min()
    last_year = df_ccaa["any"].max()
    df_first = df_ccaa[df_ccaa["any"] == first_year][["territori", "empreses"]].rename(columns={"empreses": "emp_first"})
    df_last = df_ccaa[df_ccaa["any"] == last_year][["territori", "empreses"]].rename(columns={"empreses": "emp_last"})
    df_var_ccaa = df_first.merge(df_last, on="territori")
    df_var_ccaa["var_pct"] = ((df_var_ccaa["emp_last"] / df_var_ccaa["emp_first"]) - 1) * 100
    df_var_ccaa = df_var_ccaa.sort_values("var_pct", ascending=True)

    st.subheader(f"{'Variació acumulada' if _ca else 'Variación acumulada'} {int(first_year)}-{int(last_year)} "
                 f"{'per CCAA' if _ca else 'por CCAA'}")

    fig_var = go.Figure()
    colors_var = [GREEN if v >= 0 else RED for v in df_var_ccaa["var_pct"]]
    fig_var.add_trace(go.Bar(
        y=df_var_ccaa["territori"], x=df_var_ccaa["var_pct"],
        orientation="h",
        marker_color=colors_var,
        text=[fpct(v) for v in df_var_ccaa["var_pct"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    apply_layout(fig_var,
        xaxis_title=("Variació acumulada (%)" if _ca else "Variación acumulada (%)"),
        height=max(450, len(df_var_ccaa) * 32 + 100),
        margin=dict(l=200, r=80, t=40, b=50),
    )
    fig_var.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    st.plotly_chart(fig_var, use_container_width=True)
    source("INE, DIRCE. Càlcul propi" if _ca else "INE, DIRCE. Cálculo propio")

    # Evolució temporal per CCAA seleccionades
    st.subheader(t("emp_ccaa_evolution"))

    default_ccaa = [c for c in ["Cataluña", "Madrid (Comunidad de)", "Andalucía",
                                "Comunitat Valenciana"] if c in ccaa_names]
    sel_ccaa = st.multiselect(t("emp_ccaa_select"), sorted(ccaa_names), default=default_ccaa)

    if sel_ccaa:
        fig4 = go.Figure()
        for i, ccaa in enumerate(sel_ccaa):
            df_c = df_ccaa[df_ccaa["territori"] == ccaa].sort_values("any")
            fig4.add_trace(go.Scatter(
                x=df_c["any"], y=df_c["empreses"],
                mode="lines+markers", name=ccaa,
                line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                marker=dict(size=5),
            ))

        apply_layout(fig4, yaxis_title=t("emp_count"), height=450)
        st.plotly_chart(fig4, use_container_width=True)
        source("INE, DIRCE")
else:
    st.info("No hi ha dades de CCAA disponibles." if _ca
            else "No hay datos de CCAA disponibles.")

# ─── Taula ─────────────────────────────────────────────────────

with st.expander(t("download_data")):
    st.dataframe(df, use_container_width=True)
    st.download_button("CSV", df.to_csv(index=False).encode("utf-8"), "empreses_cnae47.csv", "text/csv")

page_meta("INE, Directori Central d'Empreses (DIRCE)" if _ca
          else "INE, Directorio Central de Empresas (DIRCE)", st.session_state.lang)
