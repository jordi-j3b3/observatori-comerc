"""Pàgina destacada: Pols diari del consum (CDMGE — INE estadística experimental)."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from style import inject_css, setup_lang, page_header

inject_css()
t = setup_lang(show_selector=False)
page_header()

_ca = st.session_state.lang == "ca"


@st.cache_data(ttl=3600)
def load_cdmge():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "cdmge.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


df_cdmge = load_cdmge()

if df_cdmge.empty or "indicador" not in df_cdmge.columns:
    st.warning(
        "No hi ha dades CDMGE disponibles. Executa el processador per generar la cache."
        if _ca else
        "No hay datos CDMGE disponibles. Ejecuta el procesador para generar la caché."
    )
    st.stop()

df_cdmge["data"] = pd.to_datetime(df_cdmge["data"], errors="coerce")
_ta = (
    df_cdmge[df_cdmge["indicador"] == "tasa_anual"]
    .dropna(subset=["data", "valor"])
    .sort_values("data")
    .reset_index(drop=True)
)

if len(_ta) <= 30:
    st.warning("Sèrie insuficient per renderitzar." if _ca else "Serie insuficiente para renderizar.")
    st.stop()

_last_dt = _ta["data"].max()
_last_val = float(_ta.iloc[-1]["valor"])
_avg_7 = float(_ta.tail(7)["valor"].mean())
_avg_30 = float(_ta.tail(30)["valor"].mean())
_avg_90 = float(_ta.tail(90)["valor"].mean())
_avg_365 = float(_ta.tail(365)["valor"].mean()) if len(_ta) >= 365 else None

# ── Càlcul de retard real i propera publicació estimada ──
from datetime import datetime
_today = pd.Timestamp(datetime.now().date())
_lag_days = int((_today - _last_dt).days)

# Propera publicació INE estimada: ~25-30 dies després de fi de mes de referència.
# El darrer mes complet publicat és el del _last_dt; el següent es publicarà a finals
# del mes en curs si _last_dt ja ha passat fa més de 25 dies.
_next_month = (_last_dt + pd.offsets.MonthEnd(1)).normalize()
_next_pub_est = (_next_month + pd.Timedelta(days=28)).normalize()

# ── Capçalera ──
_eyebrow = ("GRANULARITAT DIÀRIA · PUBLICACIÓ MENSUAL" if _ca
            else "GRANULARIDAD DIARIA · PUBLICACIÓN MENSUAL")
_title = "Pols diari del consum" if _ca else "Pulso diario del consumo"
_sub = ("Sèrie diària de vendes acumulades de grans empreses del comerç al detall, "
        "comparades amb el mateix període de l'any anterior. <strong>L'INE publica aquesta "
        "sèrie un cop al mes</strong>: cada dia està disponible, però amb el retard típic de la publicació."
        if _ca else
        "Serie diaria de ventas acumuladas de grandes empresas del comercio minorista, "
        "comparadas con el mismo período del año anterior. <strong>El INE publica esta serie "
        "una vez al mes</strong>: cada día está disponible, pero con el retraso típico de la publicación.")

_asof_lbl = "Darrera dada disponible" if _ca else "Último dato disponible"
_lag_lbl = ("retard de {n} dies vs avui" if _ca else "retraso de {n} días vs hoy").format(n=_lag_days)
_next_lbl = ("Propera actualització estimada" if _ca else "Próxima actualización estimada")

st.markdown(
    f"""
    <div class="cdmge-block">
        <div class="cdmge-eyebrow"><span class="cdmge-pulse"></span>{_eyebrow}</div>
        <h3>{_title}</h3>
        <div class="cdmge-sub">{_sub}</div>
        <div class="cdmge-asof">
            {_asof_lbl}: <strong>{_last_dt.strftime("%d/%m/%Y")}</strong> ({_lag_lbl})
            &nbsp;·&nbsp; {_next_lbl}: ~{_next_pub_est.strftime("%d/%m/%Y")}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPIs ──
k1, k2, k3, k4 = st.columns(4)
k1.metric(
    ("Darrera dada" if _ca else "Último dato"),
    f"{_last_val:+.1f}%",
    delta=_last_dt.strftime("%d/%m/%Y"),
    delta_color="off",
    help=("Taxa anual de vendes diàries acumulades del darrer dia publicat per l'INE."
          if _ca else
          "Tasa anual de ventas diarias acumuladas del último día publicado por el INE."),
)
k2.metric(("Mitjana 7 dies" if _ca else "Media 7 días"), f"{_avg_7:+.1f}%",
          delta=f"{(_avg_7 - _avg_30):+.1f} pp vs 30d", delta_color="off")
k3.metric(("Mitjana 30 dies" if _ca else "Media 30 días"), f"{_avg_30:+.1f}%",
          delta=f"{(_avg_30 - _avg_90):+.1f} pp vs 90d", delta_color="off")
k4.metric(("Mitjana 90 dies" if _ca else "Media 90 días"), f"{_avg_90:+.1f}%",
          delta=(f"{(_avg_90 - _avg_365):+.1f} pp vs 365d" if _avg_365 is not None else None),
          delta_color="off")

# ── Selectors ──
sc1, sc2 = st.columns([2, 2])
with sc1:
    _periodes = {
        ("3 mesos" if _ca else "3 meses"): 90,
        ("6 mesos" if _ca else "6 meses"): 180,
        ("12 mesos" if _ca else "12 meses"): 365,
        ("24 mesos" if _ca else "24 meses"): 730,
        ("Des de 2020" if _ca else "Desde 2020"): 9999,
    }
    _per_lbl = st.radio(
        ("Període" if _ca else "Período"),
        list(_periodes.keys()),
        index=2, horizontal=True, key="cdmge_per",
    )
    _per_days = _periodes[_per_lbl]
with sc2:
    _smoothings = {
        ("Sense suavitzat" if _ca else "Sin suavizado"): 1,
        ("Mitjana mòbil 7 dies" if _ca else "Media móvil 7 días"): 7,
        ("Mitjana mòbil 30 dies" if _ca else "Media móvil 30 días"): 30,
        ("Mitjana mòbil 90 dies" if _ca else "Media móvil 90 días"): 90,
    }
    _sm_lbl = st.radio(
        ("Suavitzat" if _ca else "Suavizado"),
        list(_smoothings.keys()),
        index=2, horizontal=True, key="cdmge_sm",
    )
    _sm_days = _smoothings[_sm_lbl]

# ── Filtrar dades ──
if _per_days >= 9999:
    _plot_df = _ta.copy()
else:
    _cutoff = _last_dt - pd.Timedelta(days=_per_days)
    _plot_df = _ta[_ta["data"] >= _cutoff].copy()

_plot_df["mm"] = _plot_df["valor"].rolling(window=_sm_days, min_periods=max(1, _sm_days // 4)).mean()

# ── Gràfic ──
_fig = go.Figure()

_fig.add_trace(go.Scatter(
    x=_plot_df["data"], y=_plot_df["mm"],
    mode="lines",
    name=_sm_lbl,
    line=dict(color="#d24d2c", width=2.8),
    fill="tozeroy",
    fillcolor="rgba(210, 77, 44, 0.12)",
    hovertemplate="%{x|%d/%m/%Y}<br><b>%{y:+.1f}%</b><extra></extra>",
))

if _sm_days > 1:
    _fig.add_trace(go.Scatter(
        x=_plot_df["data"], y=_plot_df["valor"],
        mode="lines",
        name=("Diari" if _ca else "Diario"),
        line=dict(color="#999", width=0.8, dash="dot"),
        opacity=0.45,
        hovertemplate="%{x|%d/%m/%Y}: %{y:+.1f}%<extra></extra>",
    ))

_fig.add_hline(y=0, line_dash="solid", line_color="#666", line_width=1.2,
               annotation_text=("0% (sense canvi YoY)" if _ca else "0% (sin cambio YoY)"),
               annotation_position="bottom right",
               annotation_font=dict(size=10, color="#666"))

_covid_start = pd.Timestamp("2020-03-14")
_covid_end = pd.Timestamp("2020-06-21")
if _plot_df["data"].min() <= _covid_end:
    _fig.add_vrect(
        x0=_covid_start, x1=_covid_end,
        fillcolor="#999", opacity=0.08, line_width=0,
        annotation_text=("Confinament" if _ca else "Confinamiento"),
        annotation_position="top left",
        annotation_font=dict(size=10, color="#666"),
    )

_fig.update_layout(
    height=460,
    margin=dict(l=10, r=10, t=30, b=20),
    yaxis_title=("Variació anual (%)" if _ca else "Variación anual (%)"),
    xaxis_title="",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(size=11)),
    plot_bgcolor="white",
)
_fig.update_yaxes(gridcolor="#eee", zeroline=False, ticksuffix="%")
_fig.update_xaxes(gridcolor="#f5f5f5", showspikes=True, spikemode="across",
                  spikethickness=1, spikecolor="#ccc")
st.plotly_chart(_fig, use_container_width=True)

# ── Anàlisi automàtica ──
with st.expander(("Anàlisi — què diuen les dades ara mateix" if _ca
                  else "Análisis — qué dicen los datos ahora mismo"), expanded=True):
    _signe = "creixement" if _avg_30 > 0 else ("contracció" if _avg_30 < 0 else "estabilitat")
    _signe_es = "crecimiento" if _avg_30 > 0 else ("contracción" if _avg_30 < 0 else "estabilidad")

    _accel = _avg_7 - _avg_30
    if abs(_accel) < 0.5:
        _dir_ca = "estable respecte de la tendència mensual"
        _dir_es = "estable respecto a la tendencia mensual"
    elif _accel > 0:
        _dir_ca = "**accelerant** (mitjana setmanal per sobre de la mensual)"
        _dir_es = "**acelerando** (media semanal por encima de la mensual)"
    else:
        _dir_ca = "**desaccelerant** (mitjana setmanal per sota de la mensual)"
        _dir_es = "**desacelerando** (media semanal por debajo de la mensual)"

    if _avg_365 is not None:
        _vs_anual = _avg_30 - _avg_365
        if _vs_anual > 1:
            _ctxt_ca = f"per sobre del ritme mitjà de l'any (+{_vs_anual:.1f} pp)"
            _ctxt_es = f"por encima del ritmo medio del año (+{_vs_anual:.1f} pp)"
        elif _vs_anual < -1:
            _ctxt_ca = f"per sota del ritme mitjà de l'any ({_vs_anual:+.1f} pp)"
            _ctxt_es = f"por debajo del ritmo medio del año ({_vs_anual:+.1f} pp)"
        else:
            _ctxt_ca = f"alineat amb el ritme mitjà de l'any ({_vs_anual:+.1f} pp)"
            _ctxt_es = f"alineado con el ritmo medio del año ({_vs_anual:+.1f} pp)"
    else:
        _ctxt_ca = _ctxt_es = ""

    _ult_90 = _ta.tail(90)
    _max_row = _ult_90.loc[_ult_90["valor"].idxmax()]
    _min_row = _ult_90.loc[_ult_90["valor"].idxmin()]

    if _ca:
        st.markdown(f"""
**Lectura del moment**

Les vendes diàries de les grans empreses del comerç al detall mostren un **{_signe} interanual** del **{_avg_30:+.1f}%** en mitjana mòbil dels darrers 30 dies. La tendència curta (mitjana mòbil 7 dies) està {_dir_ca}.

En context anual, el ritme actual queda {_ctxt_ca}.

**Punts singulars dels darrers 90 dies**:
- Màxim diari: **{_max_row['valor']:+.1f}%** el {_max_row['data'].strftime('%d/%m/%Y')}
- Mínim diari: **{_min_row['valor']:+.1f}%** el {_min_row['data'].strftime('%d/%m/%Y')}

**Com llegir-ho**:
- Valors **positius** = les grans cadenes facturen més que fa un any (en €, sense descomptar inflació).
- Valors **propers a 0** = ritme similar a fa un any.
- Valors **molt negatius** = senyal d'alerta. Recordar el confinament 2020 (-30% a -50% sostinguts) com a referència visual.

**Avis interpretatiu**: aquesta sèrie reflecteix el comportament de **grans cadenes** (Mercadona, Inditex, El Corte Inglés, Carrefour, Lidl i similars), que solen ser **menys sensibles** a les desacceleracions cícliques que el petit comerç (efecte refugi en preu, fidelització, programes de marca). En recessions, el petit comerç pateix més; per tant, el CDMGE pot ser un indicador de **terra del cicle**, no de la mitjana sectorial.
        """)
    else:
        st.markdown(f"""
**Lectura del momento**

Las ventas diarias de las grandes empresas del comercio minorista muestran un **{_signe_es} interanual** del **{_avg_30:+.1f}%** en media móvil de los últimos 30 días. La tendencia corta (media móvil 7 días) está {_dir_es}.

En contexto anual, el ritmo actual queda {_ctxt_es}.

**Puntos singulares de los últimos 90 días**:
- Máximo diario: **{_max_row['valor']:+.1f}%** el {_max_row['data'].strftime('%d/%m/%Y')}
- Mínimo diario: **{_min_row['valor']:+.1f}%** el {_min_row['data'].strftime('%d/%m/%Y')}

**Cómo leerlo**:
- Valores **positivos** = las grandes cadenas facturan más que hace un año (en €, sin descontar inflación).
- Valores **cercanos a 0** = ritmo similar al de hace un año.
- Valores **muy negativos** = señal de alerta. Recordar el confinamiento 2020 (-30% a -50% sostenidos) como referencia visual.

**Aviso interpretativo**: esta serie refleja el comportamiento de **grandes cadenas** (Mercadona, Inditex, El Corte Inglés, Carrefour, Lidl y similares), que suelen ser **menos sensibles** a las desaceleraciones cíclicas que el pequeño comercio (efecto refugio en precio, fidelización, programas de marca). En recesiones, el pequeño comercio sufre más; el CDMGE puede ser un indicador de **suelo del ciclo**, no de la media sectorial.
        """)

# ── Metodologia ──
with st.expander(("Metodologia — com es calcula i què mesura" if _ca
                  else "Metodología — cómo se calcula y qué mide"), expanded=False):
    if _ca:
        st.markdown("""
**Font**: INE — *Mesura del Comerç Diari al per Menor de Grans Empreses (CDMGE)*. Estadística experimental publicada des de gener de 2019.

**Què mesura**: l'INE recull diàriament les vendes d'una mostra de **grans empreses del comerç al detall (CNAE 47)** a través d'un acord directe amb les principals cadenes. La mostra es manté estable per garantir comparabilitat temporal, però el resultat **no és representatiu del petit comerç**.

**Com es calcula la *taxa anual* que veus al gràfic**: per a cada dia *D*, l'INE compara les vendes acumulades del mes en curs fins al dia *D* amb les vendes acumulades del mateix període del **mateix mes de l'any anterior**. El valor és la variació percentual interanual:

> Si el 31/3/2026 surt **+9,1%**, vol dir que les vendes acumulades del 1 al 31 de març del 2026 estan un 9,1% per sobre de les del 1 al 31 de març del 2025.

**Per què suavitzem**: la sèrie diària té molt soroll (cap de setmana, festius, calendari, dies amb promocions). La **mitjana mòbil** filtra el soroll i deixa veure la tendència. Amb el selector pots triar 7, 30 o 90 dies — més finestra, més tendència estructural; menys finestra, més reactivitat als esdeveniments recents.

**Limitacions a tenir en compte**:
- Cobreix **només grans empreses** (cadenes amb cobertura nacional). El petit comerç i l'especialitzat de barri queden fora.
- Valors **nominals**: no estan deflactats per IPC, així que en períodes d'alta inflació part del creixement és preu i no volum.
- És una **estadística experimental**: la metodologia pot evolucionar i la sèrie pot revisar-se.
- No té desagregació per CCAA ni per subsector CNAE 47.

**Calendari de publicació (important)**: l'INE no publica aquesta sèrie en temps real. Es difon **un cop al mes**, normalment cap a la **darrera setmana del mes següent** al de referència (les dades de març es publiquen a finals d'abril, les d'abril a finals de maig, etc.). Per tant, en qualsevol moment estàs veient dades amb un retard típic d'**entre 25 i 55 dies** segons el dia del mes en què consultis. La granularitat és diària, però la freqüència de publicació és mensual.

**Per què la incloem aquí**: la resta del dashboard treballa amb dades anuals (PIB, VAB, EAS) o trimestrals (EPA), que arriben amb 6-18 mesos de retard. Tot i la publicació mensual, la CDMGE segueix sent la peça **més recent** disponible i, sobretot, l'única amb **detall diari** — útil per detectar canvis de ritme dins el mes (puntes Black Friday, rebaixes, Setmana Santa, Nadal) que les sèries trimestrals/anuals oculten.
        """)
    else:
        st.markdown("""
**Fuente**: INE — *Medición del Comercio Diario al por Menor de Grandes Empresas (CDMGE)*. Estadística experimental publicada desde enero de 2019.

**Qué mide**: el INE recoge diariamente las ventas de una muestra de **grandes empresas del comercio minorista (CNAE 47)** mediante acuerdo directo con las principales cadenas. La muestra se mantiene estable para garantizar comparabilidad temporal, pero el resultado **no es representativo del pequeño comercio**.

**Cómo se calcula la *tasa anual* que ves en el gráfico**: para cada día *D*, el INE compara las ventas acumuladas del mes en curso hasta el día *D* con las ventas acumuladas del mismo período del **mismo mes del año anterior**. El valor es la variación porcentual interanual:

> Si el 31/3/2026 sale **+9,1%**, significa que las ventas acumuladas del 1 al 31 de marzo de 2026 están un 9,1% por encima de las del 1 al 31 de marzo de 2025.

**Por qué suavizamos**: la serie diaria tiene mucho ruido (fin de semana, festivos, calendario, días con promociones). La **media móvil** filtra el ruido y deja ver la tendencia. Con el selector puedes elegir 7, 30 o 90 días — más ventana, más tendencia estructural; menos ventana, más reactividad a eventos recientes.

**Limitaciones a tener en cuenta**:
- Cubre **solo grandes empresas** (cadenas con cobertura nacional). El pequeño comercio y el especializado de barrio quedan fuera.
- Valores **nominales**: no están deflactados por IPC, así que en períodos de alta inflación parte del crecimiento es precio y no volumen.
- Es una **estadística experimental**: la metodología puede evolucionar y la serie puede revisarse.
- No tiene desagregación por CCAA ni por subsector CNAE 47.

**Calendario de publicación (importante)**: el INE no publica esta serie en tiempo real. Se difunde **una vez al mes**, normalmente hacia la **última semana del mes siguiente** al de referencia (los datos de marzo se publican a finales de abril, los de abril a finales de mayo, etc.). Por tanto, en cualquier momento estás viendo datos con un retraso típico de **entre 25 y 55 días** según el día del mes en que consultes. La granularidad es diaria, pero la frecuencia de publicación es mensual.

**Por qué la incluimos aquí**: el resto del dashboard trabaja con datos anuales (PIB, VAB, EAS) o trimestrales (EPA), que llegan con 6-18 meses de retraso. A pesar de la publicación mensual, la CDMGE sigue siendo la pieza **más reciente** disponible y, sobre todo, la única con **detalle diario** — útil para detectar cambios de ritmo dentro del mes (picos Black Friday, rebajas, Semana Santa, Navidad) que las series trimestrales/anuales ocultan.
        """)

st.caption(
    ("Font: INE — Mesura del Comerç Diari al per Menor de Grans Empreses (CDMGE), estadística experimental. "
     "Sèrie diària des del gener de 2019."
     if _ca else
     "Fuente: INE — Medición del Comercio Diario al por Menor de Grandes Empresas (CDMGE), estadística experimental. "
     "Serie diaria desde enero de 2019.")
)
