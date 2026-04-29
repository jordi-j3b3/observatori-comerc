"""Pagina 9: Subsectors del comerc al detall (CNAE 47 a 3 digits + despesa familiar)"""
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

# ─── Càrrega de dades ────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_csv(name, code_col=None, code_pad=0):
    """Llegeix CSV i converteix la columna de codi a string (amb zfill opcional per COICOP)."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "cache", f"{name}.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    if code_col and code_col in df.columns:
        df[code_col] = df[code_col].astype(str).str.zfill(code_pad) if code_pad else df[code_col].astype(str)
    return df


df_dirce = load_csv("subsectors_dirce", code_col="codi")
df_eas = load_csv("subsectors_eas", code_col="codi")
df_epf = load_csv("subsectors_epf", code_col="codi_coicop", code_pad=2)

# ─── Etiquetes (bilingue) ───────────────────────────────────

SUBSECTOR_LABELS = {
    "ca": {
        "47":  "CNAE 47 (total)",
        "471": "Establiments no especialitzats",
        "472": "Alimentació, begudes i tabac",
        "474": "Equips TIC",
        "475": "Articles d'ús domèstic",
        "476": "Cultura i recreatius",
        "477": "Vestit, calçat i altres",
        "478": "Mercadillos",
        "479": "E-commerce i venda directa",
    },
    "es": {
        "47":  "CNAE 47 (total)",
        "471": "Estab. no especializados",
        "472": "Alimentación, bebidas y tabaco",
        "474": "Equipos TIC",
        "475": "Artículos de uso doméstico",
        "476": "Cultura y recreativos",
        "477": "Vestido, calzado y otros",
        "478": "Mercadillos",
        "479": "E-commerce y venta directa",
    },
}

# Codi CNAE a excloure de la pagina (sense interes per a una analisi de retail)
EXCLUDE_CODES = ["473"]

# Exemples concrets per a cada subsector (mostrats al hover de cada barra)
SUBSECTOR_EXAMPLES = {
    "ca": {
        "471": "Supermercats (Mercadona, Caprabo, Consum, Bonpreu), hipermercats (Carrefour, Alcampo, Eroski Center, Hipercor), descompte (Lidl, Aldi, Dia), grans magatzems (El Corte Inglés), tot a 1€ (Action, Tedi, Primaprix), botigues de barri i 24h",
        "472": "Forns i pastisseries, carnisseries, peixateries, fruiteries, queviures, estancs, herbolaris, vinateries i cellers especialitzats",
        "474": "Botigues d'electrònica (MediaMarkt, FNAC), informàtica (PcComponentes botiga física), telefonia (Phone House), botigues d'operadors (Movistar, Vodafone, Orange)",
        "475": "Mobles i decoració (Ikea, Conforama, Maisons du Monde), il·luminació, parament de la llar, electrodomèstics blancs, ferreteries i bricolatge (Leroy Merlin, Bauhaus)",
        "476": "Llibreries (Casa del Libro, FNAC llibres), jugueteries (Imaginarium, ToysRUs, Drim), música, esports (Decathlon, Intersport, Forum Sport), papereries i material d'oficina",
        "477": "Roba i moda (Inditex, Mango, H&M, Primark), calçat (Camper, Kalenji), farmàcies, joieria i rellotgeria, cosmètica i perfumeria (Sephora, Druni), òptiques, regals, articles per a animals",
        "478": "Mercats setmanals i mercadillos a la via pública: alimentació, roba, antiguitats, encants",
        "479": "Comerç electrònic pure-play (PcComponentes, Privalia, Hawkers, Tradeinn), venda per correspondència, vending (màquines expenedores), venda a domicili (porta a porta, telefònica), subhastes presencials",
    },
    "es": {
        "471": "Supermercados (Mercadona, Caprabo, Consum, Bonpreu), hipermercados (Carrefour, Alcampo, Eroski Center, Hipercor), descuento (Lidl, Aldi, Dia), grandes almacenes (El Corte Inglés), todo a 1€ (Action, Tedi, Primaprix), tiendas de barrio y 24h",
        "472": "Panaderías y pastelerías, carnicerías, pescaderías, fruterías, ultramarinos, estancos, herbolarios, vinaterías y bodegas especializadas",
        "474": "Tiendas de electrónica (MediaMarkt, FNAC), informática (PcComponentes tienda física), telefonía (Phone House), tiendas de operadores (Movistar, Vodafone, Orange)",
        "475": "Muebles y decoración (Ikea, Conforama, Maisons du Monde), iluminación, menaje del hogar, electrodomésticos, ferreterías y bricolaje (Leroy Merlin, Bauhaus)",
        "476": "Librerías (Casa del Libro, FNAC libros), jugueterías (Imaginarium, ToysRUs, Drim), música, deportes (Decathlon, Intersport, Forum Sport), papelerías y material de oficina",
        "477": "Ropa y moda (Inditex, Mango, H&M, Primark), calzado (Camper, Kalenji), farmacias, joyería y relojería, cosmética y perfumería (Sephora, Druni), ópticas, regalos, artículos para animales",
        "478": "Mercados semanales y mercadillos en la vía pública: alimentación, ropa, antigüedades, rastros",
        "479": "E-commerce pure-play (PcComponentes, Privalia, Hawkers, Tradeinn), venta por correspondencia, vending (máquinas expendedoras), venta a domicilio (puerta a puerta, telefónica), subastas presenciales",
    },
}


def wrap_text(text, width=70):
    """Trenca un text en linies de longitud maxima per a hover de Plotly."""
    import textwrap
    return "<br>".join(textwrap.wrap(text, width=width))

COICOP_LABELS = {
    "ca": {
        "00": "Total despesa",
        "01": "Aliments i begudes no alc.",
        "02": "Begudes alc., tabac",
        "03": "Vestit i calçat",
        "04": "Habitatge i energia",
        "05": "Mobles i articles llar",
        "06": "Sanitat",
        "07": "Transport",
        "08": "Informació i comunicacions",
        "09": "Oci, cultura i esport",
        "10": "Educació",
        "11": "Restauració i allotjament",
        "12": "Cura personal i altres",
    },
    "es": {
        "00": "Total gasto",
        "01": "Alim. y bebidas no alc.",
        "02": "Bebidas alc., tabaco",
        "03": "Vestido y calzado",
        "04": "Vivienda y energía",
        "05": "Muebles y hogar",
        "06": "Sanidad",
        "07": "Transporte",
        "08": "Información y com.",
        "09": "Ocio, cultura y deporte",
        "10": "Educación",
        "11": "Rest. y alojamiento",
        "12": "Cuidado personal y otros",
    },
}

# Etiqueta de subsector CNAE corresponent a cada categoria de despesa familiar
# (per homogeneitzar amb les pestanyes Estructura i Activitat)
DEMAND_CNAE_LABELS = {
    "ca": {
        "01": "Alimentació (especialitzada + no especialitzada)",
        "02": "Alimentació, begudes i tabac",
        "03": "Vestit, calçat i altres",
        "05": "Articles d'ús domèstic",
        "06": "Vestit, calçat i altres (farmàcies)",
        "08": "Equips TIC",
        "09": "Cultura i recreatius",
        "12": "Vestit, calçat i altres (cosmètics)",
    },
    "es": {
        "01": "Alimentación (especializada + no especializada)",
        "02": "Alimentación, bebidas y tabaco",
        "03": "Vestido, calzado y otros",
        "05": "Artículos de uso doméstico",
        "06": "Vestido, calzado y otros (farmacias)",
        "08": "Equipos TIC",
        "09": "Cultura y recreativos",
        "12": "Vestido, calzado y otros (cosméticos)",
    },
}

# Mapeig COICOP -> CNAE 47 (categories de despesa familiar que es compren al comerc al detall)
COICOP_TO_CNAE = {
    "01": ["471", "472"],  # Aliments → no especialitzats + alimentacio especialitzada
    "02": ["472"],         # Begudes alc., tabac → estanc + begudes
    "03": ["477"],         # Vestit i calcat → 4771, 4772 (dins 477)
    "05": ["475"],         # Mobles i articles llar
    "06": ["477"],         # Sanitat → farmacia 4773 (dins 477)
    "08": ["474"],         # Info/comunicacions → equips TIC
    "09": ["476"],         # Oci, cultura → llibreries, jugueteries, esports
    "12": ["477"],         # Cura personal → cosmetics 4775 (dins 477)
}

LANG = "ca" if _ca else "es"
SLABEL = SUBSECTOR_LABELS[LANG]
SEXAMPLES = {k: wrap_text(v) for k, v in SUBSECTOR_EXAMPLES[LANG].items()}
CLABEL = COICOP_LABELS[LANG]
DLABEL = DEMAND_CNAE_LABELS[LANG]  # subsector CNAE per a la pestanya Demanda
HOVER_LBL_EX = "Exemples" if _ca else "Ejemplos"

# ─── Capçalera ──────────────────────────────────────────────

st.title("Subsectors del comerç al detall" if _ca else "Subsectores del comercio minorista")

if _ca:
    intro(
        "El CNAE 47 agrupa diversos subsectors a tres dígits amb dinàmiques molt diferents: "
        "des dels <strong>establiments no especialitzats</strong> (supermercats, hipermercats) fins al "
        "<strong>comerç electrònic</strong> (CNAE 479) o la <strong>venda en mercadillos</strong>. "
        "S'exclou el CNAE 473 (combustibles per a l'automoció) per la seva naturalesa atípica dins "
        "del comerç al detall (preus regulats, dinàmica energètica). "
        "Aquesta pàgina creua tres fonts oficials de l'INE per oferir una radiografia tridimensional: "
        "<strong>Directori d'Empreses</strong> (estructura empresarial), "
        "<strong>Enquesta Estructural d'Empreses</strong> (oferta: xifra de negoci, valor afegit, "
        "ocupació) i <strong>Enquesta de Pressupostos Familiars</strong> (demanda: despesa de les "
        "llars per tipus de béns)."
    )
else:
    intro(
        "El CNAE 47 agrupa varios subsectores a tres dígitos con dinámicas muy diferentes: "
        "desde los <strong>establecimientos no especializados</strong> (super/hipermercados) hasta el "
        "<strong>comercio electrónico</strong> (CNAE 479) o la <strong>venta en mercadillos</strong>. "
        "Se excluye el CNAE 473 (combustibles para automoción) por su naturaleza atípica dentro "
        "del comercio minorista (precios regulados, dinámica energética). "
        "Esta página cruza tres fuentes oficiales del INE para ofrecer una radiografía tridimensional: "
        "<strong>Directorio de Empresas</strong> (estructura empresarial), "
        "<strong>Encuesta Estructural de Empresas</strong> (oferta: cifra de negocios, valor añadido, "
        "empleo) y <strong>Encuesta de Presupuestos Familiares</strong> (demanda: gasto de los "
        "hogares por tipo de bienes)."
    )

if df_dirce.empty and df_eas.empty and df_epf.empty:
    st.warning("No hi ha dades disponibles." if _ca else "No hay datos disponibles.")
    st.stop()

# ─── KPIs superiors ──────────────────────────────────────────

if not df_dirce.empty:
    last_year_dirce = int(df_dirce["any"].max())
    df_last_dirce = df_dirce[df_dirce["any"] == last_year_dirce]
    df_subs_dirce = df_last_dirce[
        (df_last_dirce["codi"] != "47") & (~df_last_dirce["codi"].isin(EXCLUDE_CODES))
    ].copy()

    if not df_subs_dirce.empty:
        top_subs = df_subs_dirce.sort_values("empreses", ascending=False).iloc[0]
        total_47 = df_last_dirce[df_last_dirce["codi"] == "47"]["empreses"].sum()
        share_top = top_subs["empreses"] / total_47 * 100 if total_47 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            f"{'Subsectors CNAE 47' if _ca else 'Subsectores CNAE 47'}",
            f"{df_subs_dirce['codi'].nunique()}",
        )
        col2.metric(
            f"{'Empreses CNAE 47' if _ca else 'Empresas CNAE 47'} ({last_year_dirce})",
            fnum(total_47),
        )
        col3.metric(
            f"{'Subsector amb més empreses' if _ca else 'Subsector con más empresas'}",
            SLABEL.get(top_subs["codi"], top_subs["codi"]),
            help=("Lideratge mesurat pel nombre d'empreses. En facturació i ocupació, el "
                  "subsector líder és sovint un altre (vegeu pestanya Activitat).") if _ca else
                 ("Liderazgo medido por número de empresas. En facturación y empleo, el "
                  "subsector líder suele ser otro (ver pestaña Actividad)."),
        )
        col4.metric(
            f"{'% del total empreses' if _ca else '% del total empresas'} ({last_year_dirce})",
            fpct(share_top, 1, sign=False),
        )

st.markdown("---")

# ─── TABS ────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    ("Estructura empresarial" if _ca else "Estructura empresarial"),
    ("Activitat i productivitat" if _ca else "Actividad y productividad"),
    ("Demanda (despesa famílies)" if _ca else "Demanda (gasto familias)"),
])

# ============================================================
# TAB 1: ESTRUCTURA - DIRCE
# ============================================================
with tab1:
    if df_dirce.empty:
        st.info("Sense dades DIRCE." if _ca else "Sin datos DIRCE.")
    else:
        st.subheader("Empreses per subsector" if _ca else "Empresas por subsector")

        last_year = int(df_dirce["any"].max())
        df_subs = df_dirce[
            (df_dirce["codi"] != "47") & (df_dirce["any"] == last_year)
            & (~df_dirce["codi"].isin(EXCLUDE_CODES))
        ].copy()
        df_subs["label"] = df_subs["codi"].map(SLABEL)
        df_subs["examples"] = df_subs["codi"].map(SEXAMPLES).fillna("")
        df_subs = df_subs.sort_values("empreses", ascending=True)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=df_subs["label"], x=df_subs["empreses"],
            orientation="h",
            marker_color=PURPLE,
            text=[fnum(v) for v in df_subs["empreses"]],
            textposition="outside",
            textfont=dict(size=11),
            customdata=df_subs[["examples"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"<i>{HOVER_LBL_EX}:</i> "
                "%{customdata[0]}<br>"
                + ("<b>Empreses</b>: " if _ca else "<b>Empresas</b>: ")
                + "%{x:,.0f}<extra></extra>"
            ).replace(",", "."),
        ))
        apply_layout(fig_bar,
            title=f"{'Empreses per subsector' if _ca else 'Empresas por subsector'} ({last_year})",
            xaxis_title=("Empreses" if _ca else "Empresas"),
            height=max(420, len(df_subs) * 38 + 100),
            margin=dict(l=240, r=100, t=50, b=50),
            hovermode="closest",
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        source("INE, Directori Central d'Empreses (DIRCE), taula 73019" if _ca
               else "INE, Directorio Central de Empresas (DIRCE), tabla 73019")

        if _ca:
            st.caption(
                "**CNAE 471 — Establiments no especialitzats:** botigues que venen una varietat "
                "àmplia de productes sota un mateix sostre, sense estar especialitzades en una "
                "sola categoria. Inclou **supermercats** (Mercadona, Caprabo, Consum, Bonpreu), "
                "**hipermercats** (Carrefour, Alcampo, Eroski Center, Hipercor), **botigues de "
                "descompte** (Lidl, Aldi, Dia), **botigues de barri/24h**, **grans magatzems** "
                "(El Corte Inglés) i **botigues de tot a 1€** (Action, Tedi, Primaprix). "
                "És el subsector amb més facturació del comerç al detall espanyol per concentrar "
                "la cistella alimentària quotidiana.\n\n"
                "**CNAE 479 — E-commerce i venda directa:** comerç al detall per internet o "
                "correspondència, vending, venda a domicili (porta a porta), subhastes presencials "
                "i venda telefònica. **No inclou** el comerç online d'empreses tradicionals amb "
                "botiga física: aquestes vendes online es comptabilitzen al subsector principal "
                "de l'empresa (ex: Carrefour online → 471, Decathlon online → 4764 dins 476). "
                "**Per això CNAE 479 NO coincideix amb el volum d'e-commerce de la pàgina "
                "E-commerce** (font CNMC): el 2024 el CNAE 479 (17.181 M€) representa només un "
                "67% del volum CNMC (25.739 M€). Veure detall a la pàgina Metodologia."
            )
        else:
            st.caption(
                "**CNAE 471 — Establecimientos no especializados:** tiendas que venden una "
                "variedad amplia de productos bajo un mismo techo, sin estar especializadas en "
                "una sola categoría. Incluye **supermercados** (Mercadona, Caprabo, Consum, "
                "Bonpreu), **hipermercados** (Carrefour, Alcampo, Eroski Center, Hipercor), "
                "**tiendas de descuento** (Lidl, Aldi, Dia), **tiendas de barrio/24h**, **grandes "
                "almacenes** (El Corte Inglés) y **tiendas de todo a 1€** (Action, Tedi, "
                "Primaprix). Es el subsector con mayor facturación del comercio al detalle "
                "español por concentrar la cesta alimentaria cotidiana.\n\n"
                "**CNAE 479 — E-commerce y venta directa:** comercio minorista por internet o "
                "correspondencia, vending, venta a domicilio (puerta a puerta), subastas "
                "presenciales y venta telefónica. **No incluye** el comercio online de empresas "
                "tradicionales con tienda física: esas ventas online se contabilizan en el "
                "subsector principal de la empresa (ej: Carrefour online → 471, Decathlon online "
                "→ 4764 dentro de 476). **Por eso CNAE 479 NO coincide con el volumen de "
                "e-commerce de la página E-commerce** (fuente CNMC): en 2024 el CNAE 479 "
                "(17.181 M€) representa solo un 67% del volumen CNMC (25.739 M€). Ver detalle "
                "en la página Metodología."
            )

        # Evolució per subsector
        st.subheader("Evolució per subsector" if _ca else "Evolución por subsector")

        first_year = int(df_dirce["any"].min())
        df_first = df_dirce[
            (df_dirce["codi"] != "47") & (df_dirce["any"] == first_year)
            & (~df_dirce["codi"].isin(EXCLUDE_CODES))
        ][["codi", "empreses"]].rename(columns={"empreses": "emp_first"})
        df_last = df_dirce[
            (df_dirce["codi"] != "47") & (df_dirce["any"] == last_year)
            & (~df_dirce["codi"].isin(EXCLUDE_CODES))
        ][["codi", "empreses"]].rename(columns={"empreses": "emp_last"})
        df_var = df_first.merge(df_last, on="codi")
        df_var["var_pct"] = ((df_var["emp_last"] / df_var["emp_first"]) - 1) * 100
        df_var["label"] = df_var["codi"].map(SLABEL)
        df_var["examples"] = df_var["codi"].map(SEXAMPLES).fillna("")
        df_var = df_var.sort_values("var_pct", ascending=True)

        fig_var = go.Figure()
        colors = [GREEN if v >= 0 else RED for v in df_var["var_pct"]]
        fig_var.add_trace(go.Bar(
            y=df_var["label"], x=df_var["var_pct"],
            orientation="h",
            marker_color=colors,
            text=[fpct(v) for v in df_var["var_pct"]],
            textposition="outside",
            textfont=dict(size=11),
            customdata=df_var[["examples"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"<i>{HOVER_LBL_EX}:</i> "
                "%{customdata[0]}<br>"
                + ("<b>Variació</b>: " if _ca else "<b>Variación</b>: ")
                + "%{x:.1f}%<extra></extra>"
            ),
        ))
        apply_layout(fig_var,
            title=f"{'Variació' if _ca else 'Variación'} {first_year}-{last_year} (%)",
            xaxis_title="%",
            height=max(420, len(df_var) * 38 + 100),
            margin=dict(l=240, r=80, t=50, b=50),
            hovermode="closest",
        )
        fig_var.add_vline(x=0, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        st.plotly_chart(fig_var, use_container_width=True)
        source("INE, DIRCE. Càlcul propi" if _ca else "INE, DIRCE. Cálculo propio")

        # ── Insight estructural (analisi profunda) ─────────────
        leader = df_subs.iloc[-1]
        runner = df_subs.iloc[-2] if len(df_subs) >= 2 else None
        loser = df_var.iloc[0]
        winner = df_var.iloc[-1]

        # Concentracio top-3 vs base llarga
        df_subs_desc = df_subs.sort_values("empreses", ascending=False).reset_index(drop=True)
        total_subs = df_subs_desc["empreses"].sum()
        top3_share = df_subs_desc.head(3)["empreses"].sum() / total_subs * 100 if total_subs else 0

        # Subsectors que creixen vs perden
        n_grow = int((df_var["var_pct"] >= 0).sum())
        n_lose = int((df_var["var_pct"] < 0).sum())

        # Variacio mitjana ponderada
        emp_first_total = df_var["emp_first"].sum()
        emp_last_total = df_var["emp_last"].sum()
        var_total = (emp_last_total / emp_first_total - 1) * 100 if emp_first_total else 0

        if _ca:
            insight(
                f"El comerç al detall espanyol agrupa <strong>{fnum(total_subs)} empreses</strong> en "
                f"<strong>{len(df_subs)} subsectors</strong>. <strong>{leader['label']}</strong> "
                f"és el que té més empreses ({fnum(leader['empreses'])}), seguit de "
                f"<strong>{runner['label'] if runner is not None else '—'}</strong>"
                + (f" ({fnum(runner['empreses'])})" if runner is not None else "")
                + f". Els tres subsectors amb més empreses concentren un "
                f"<strong>{fpct(top3_share, 1, sign=False)}</strong> del total — un nivell de "
                f"concentració moderat per la naturalesa fragmentada del comerç de proximitat. "
                f"<br><br>"
                f"Entre {first_year} i {last_year}, el sector ha perdut un "
                f"<strong>{fpct(var_total, 1)}</strong> d'empreses en agregat. La dinàmica és "
                f"asimètrica: <strong>{n_grow} subsector{'s' if n_grow != 1 else ''} creixen</strong> i "
                f"<strong>{n_lose} subsector{'s' if n_lose != 1 else ''} perden</strong> teixit "
                f"empresarial. <strong>{winner['label']}</strong> lidera el creixement "
                f"({fpct(winner['var_pct'])}), una xifra coherent amb el desplaçament del consum cap "
                f"a canals digitals i nous formats de proximitat. <strong>{loser['label']}</strong> "
                f"és el que més pateix ({fpct(loser['var_pct'])}), un patró típic dels subsectors amb "
                f"més pressió de la digitalització i del comerç de gran format. "
                f"<br><br>"
                f"<em>Lectura amb les altres pestanyes:</em> el rànquing per <strong>nombre d'empreses</strong> "
                f"no és el mateix que el rànquing per <strong>facturació</strong> o per "
                f"<strong>ocupació</strong>. Els subsectors amb molts establiments petits (vestit, "
                f"alimentació especialitzada) tenen molt més pes en empreses que en xifra de negoci. "
                f"Els no especialitzats, al revés, dominen en facturació amb un nombre relativament reduït "
                f"d'empreses (consolidació en grans operadors). Veure pestanya Activitat per a la "
                f"comparativa."
            )
        else:
            insight(
                f"El comercio al detalle español agrupa <strong>{fnum(total_subs)} empresas</strong> en "
                f"<strong>{len(df_subs)} subsectores</strong>. <strong>{leader['label']}</strong> "
                f"es el que tiene más empresas ({fnum(leader['empreses'])}), seguido de "
                f"<strong>{runner['label'] if runner is not None else '—'}</strong>"
                + (f" ({fnum(runner['empreses'])})" if runner is not None else "")
                + f". Los tres subsectores con más empresas concentran un "
                f"<strong>{fpct(top3_share, 1, sign=False)}</strong> del total — un nivel de "
                f"concentración moderado por la naturaleza fragmentada del comercio de proximidad. "
                f"<br><br>"
                f"Entre {first_year} y {last_year}, el sector ha perdido un "
                f"<strong>{fpct(var_total, 1)}</strong> de empresas en agregado. La dinámica es "
                f"asimétrica: <strong>{n_grow} subsector{'es' if n_grow != 1 else ''} crecen</strong> y "
                f"<strong>{n_lose} subsector{'es' if n_lose != 1 else ''} pierden</strong> tejido "
                f"empresarial. <strong>{winner['label']}</strong> lidera el crecimiento "
                f"({fpct(winner['var_pct'])}), una cifra coherente con el desplazamiento del consumo "
                f"hacia canales digitales y nuevos formatos de proximidad. <strong>{loser['label']}</strong> "
                f"es el que más sufre ({fpct(loser['var_pct'])}), un patrón típico de los subsectores con "
                f"más presión de la digitalización y del comercio de gran formato. "
                f"<br><br>"
                f"<em>Lectura con las otras pestañas:</em> el ranking por <strong>número de empresas</strong> "
                f"no coincide con el ranking por <strong>facturación</strong> o por "
                f"<strong>empleo</strong>. Los subsectores con muchos establecimientos pequeños (vestido, "
                f"alimentación especializada) pesan mucho más en empresas que en cifra de negocios. "
                f"Los no especializados, al revés, dominan en facturación con un número relativamente "
                f"reducido de empresas (consolidación en grandes operadores). Ver pestaña Actividad para "
                f"la comparativa."
            )

# ============================================================
# TAB 2: ACTIVITAT I PRODUCTIVITAT - EAS
# ============================================================
with tab2:
    if df_eas.empty:
        st.info("Sense dades disponibles." if _ca else "Sin datos disponibles.")
    else:
        last_year = int(df_eas["any"].max())
        df_last = df_eas[df_eas["any"] == last_year].copy()
        df_subs = df_last[
            (df_last["codi"] != "47") & (~df_last["codi"].isin(EXCLUDE_CODES))
        ].copy()
        df_subs["label"] = df_subs["codi"].map(SLABEL)
        df_subs["examples"] = df_subs["codi"].map(SEXAMPLES).fillna("")

        if _ca:
            st.caption(
                "**Notes metodològiques.** *Inclou comerç electrònic*: l'Enquesta Estructural d'Empreses "
                "recull totes les empreses CNAE 47, incloent el comerç electrònic pur (CNAE 479) i les "
                "vendes online d'establiments tradicionals (que es comptabilitzen al seu subsector "
                "principal). *Preus corrents*: les magnituds es mostren a preus de cada any (no "
                "deflactades). Per a una comparació real amb la pàgina Productivitat, cal aplicar el "
                "deflactor IPC. *Coincidència amb altres apartats*: el Personal coincideix amb la pàgina "
                "Productivitat; la suma dels subsectors té un gap del 0,5–1% respecte al total CNAE 47 "
                "per arrodoniments estadístics de la mateixa enquesta."
            )
        else:
            st.caption(
                "**Notas metodológicas.** *Incluye comercio electrónico*: la Encuesta Estructural de "
                "Empresas recoge todas las empresas CNAE 47, incluyendo el comercio electrónico puro "
                "(CNAE 479) y las ventas online de establecimientos tradicionales (contabilizadas en su "
                "subsector principal). *Precios corrientes*: las magnitudes se muestran a precios de "
                "cada año (sin deflactar). Para una comparación real con la página Productividad, "
                "aplicar el deflactor IPC. *Coincidencia con otros apartados*: el Personal coincide con "
                "la página Productividad; la suma de subsectores tiene un gap del 0,5–1% respecto al "
                "total CNAE 47 por redondeos estadísticos de la misma encuesta."
            )

        st.subheader(f"{'Xifra de negoci per subsector' if _ca else 'Cifra de negocios por subsector'} ({last_year})")

        df_xn = df_subs.sort_values("xifra_negoci", ascending=True)
        fig_xn = go.Figure()
        fig_xn.add_trace(go.Bar(
            y=df_xn["label"], x=df_xn["xifra_negoci"] / 1e9,
            orientation="h",
            marker_color=PURPLE,
            text=[f"{v/1e9:.1f}".replace(".", ",") + " M€" for v in df_xn["xifra_negoci"]],
            textposition="outside",
            textfont=dict(size=11),
            customdata=df_xn[["examples"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"<i>{HOVER_LBL_EX}:</i> "
                "%{customdata[0]}<br>"
                + ("<b>Xifra de negoci</b>: " if _ca else "<b>Cifra de negocios</b>: ")
                + "%{x:.2f} k milions €<extra></extra>"
            ),
        ))
        apply_layout(fig_xn,
            xaxis_title=("Xifra de negoci (k milions €)" if _ca else "Cifra de negocios (mil millones €)"),
            height=max(420, len(df_xn) * 38 + 100),
            margin=dict(l=240, r=120, t=40, b=50),
            hovermode="closest",
        )
        st.plotly_chart(fig_xn, use_container_width=True)
        source("INE, Enquesta Estructural d'Empreses Sector Comerç, taula 76818" if _ca
               else "INE, Encuesta Estructural de Empresas Sector Comercio, tabla 76818")

        # Productivitat: VA per persona ocupada
        st.subheader(f"{'Productivitat (VA per persona ocupada)' if _ca else 'Productividad (VA por persona ocupada)'} ({last_year})")

        df_pr = df_subs.copy()
        df_pr["productivitat"] = df_pr["valor_afegit"] / df_pr["personal_ocupat"]
        df_pr = df_pr.sort_values("productivitat", ascending=True)

        # Mitjana ponderada dels subsectors mostrats (exclou 473)
        va_sum = df_subs["valor_afegit"].sum()
        per_sum = df_subs["personal_ocupat"].sum()
        avg_prod = va_sum / per_sum if per_sum else None

        fig_pr = go.Figure()
        fig_pr.add_trace(go.Bar(
            y=df_pr["label"], x=df_pr["productivitat"],
            orientation="h",
            marker_color=ORANGE,
            text=[f"{v/1000:.1f}".replace(".", ",") + "k€" for v in df_pr["productivitat"]],
            textposition="outside",
            textfont=dict(size=11),
            customdata=df_pr[["examples"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"<i>{HOVER_LBL_EX}:</i> "
                "%{customdata[0]}<br>"
                + ("<b>Productivitat</b>: " if _ca else "<b>Productividad</b>: ")
                + "%{x:,.0f} €/ocupat<extra></extra>"
            ).replace(",", "."),
        ))
        if avg_prod:
            fig_pr.add_vline(
                x=avg_prod, line_dash="dash", line_color=PURPLE, line_width=2,
                annotation_text=f"{'Mitjana subsectors' if _ca else 'Media subsectores'}: {avg_prod/1000:.1f}k€".replace(".", ","),
                annotation_position="top right",
            )
        apply_layout(fig_pr,
            xaxis_title=("VA / persona ocupada (€)" if _ca else "VA / persona ocupada (€)"),
            height=max(420, len(df_pr) * 38 + 100),
            margin=dict(l=240, r=180, t=40, b=50),
            hovermode="closest",
        )
        st.plotly_chart(fig_pr, use_container_width=True)
        source("INE, Enquesta Estructural d'Empreses Sector Comerç. Càlcul propi" if _ca
               else "INE, Encuesta Estructural de Empresas Sector Comercio. Cálculo propio")

        # Personal ocupat
        st.subheader(f"{'Persones ocupades per subsector' if _ca else 'Personas ocupadas por subsector'} ({last_year})")

        df_per = df_subs.sort_values("personal_ocupat", ascending=True)
        fig_per = go.Figure()
        fig_per.add_trace(go.Bar(
            y=df_per["label"], x=df_per["personal_ocupat"],
            orientation="h",
            marker_color=GREEN,
            text=[fnum(v) for v in df_per["personal_ocupat"]],
            textposition="outside",
            textfont=dict(size=11),
            customdata=df_per[["examples"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"<i>{HOVER_LBL_EX}:</i> "
                "%{customdata[0]}<br>"
                + ("<b>Persones ocupades</b>: " if _ca else "<b>Personas ocupadas</b>: ")
                + "%{x:,.0f}<extra></extra>"
            ).replace(",", "."),
        ))
        apply_layout(fig_per,
            xaxis_title=("Persones ocupades" if _ca else "Personas ocupadas"),
            height=max(420, len(df_per) * 38 + 100),
            margin=dict(l=240, r=120, t=40, b=50),
            hovermode="closest",
        )
        st.plotly_chart(fig_per, use_container_width=True)
        source("INE, Enquesta Estructural d'Empreses Sector Comerç" if _ca
               else "INE, Encuesta Estructural de Empresas Sector Comercio")

        # ── Insight productivitat (analisi profunda) ──────────
        top_pr = df_pr.iloc[-1]
        bot_pr = df_pr.iloc[0]
        ratio_pr = top_pr["productivitat"] / bot_pr["productivitat"] if bot_pr["productivitat"] else 0

        # Concentracio: subsector amb mes xifra negoci i quina quota representa
        df_xn_desc = df_subs.sort_values("xifra_negoci", ascending=False).reset_index(drop=True)
        top_xn = df_xn_desc.iloc[0]
        total_xn = df_subs["xifra_negoci"].sum()
        share_top_xn = top_xn["xifra_negoci"] / total_xn * 100 if total_xn else 0

        # Subsector mes intensiu en ma d'obra (mes ocupats per cada milio de XN)
        df_subs_ratio = df_subs.copy()
        df_subs_ratio["intensitat_laboral"] = df_subs_ratio["personal_ocupat"] / (df_subs_ratio["xifra_negoci"] / 1e6)
        most_labor = df_subs_ratio.sort_values("intensitat_laboral", ascending=False).iloc[0]
        least_labor = df_subs_ratio.sort_values("intensitat_laboral", ascending=True).iloc[0]

        # Empreses mitjanes (xifra negoci / nombre empreses)
        df_subs_size = df_subs.copy()
        if "n_empreses_eas" in df_subs_size.columns:
            df_subs_size["xn_per_empresa"] = df_subs_size["xifra_negoci"] / df_subs_size["n_empreses_eas"]
            biggest = df_subs_size.sort_values("xn_per_empresa", ascending=False).iloc[0]
            smallest = df_subs_size.sort_values("xn_per_empresa", ascending=True).iloc[0]
        else:
            biggest = smallest = None

        if _ca:
            txt = (
                f"<strong>{top_xn['label']}</strong> domina la facturació del comerç al detall espanyol "
                f"amb <strong>{top_xn['xifra_negoci']/1e9:.1f} k milions €</strong>".replace(".", ",")
                + f" — un <strong>{fpct(share_top_xn, 1, sign=False)}</strong> del total. "
                f"Aquesta concentració contrasta amb el rànquing per nombre d'empreses (vegeu pestanya "
                f"Estructura empresarial): hi ha pocs operadors molt grans (Mercadona, Carrefour, El "
                f"Corte Inglés, Lidl) que mouen el gruix del volum. "
                f"<br><br>"
                f"<strong>Dispersió de la productivitat:</strong> "
                f"<strong>{top_pr['label']}</strong> ({top_pr['productivitat']/1000:.1f}k€".replace(".", ",")
                + f" de VA per ocupat) genera "
                f"<strong>{ratio_pr:.1f}".replace(".", ",")
                + f" vegades més valor</strong> per persona que <strong>{bot_pr['label']}</strong> "
                f"({bot_pr['productivitat']/1000:.1f}k€)".replace(".", ",") + ". "
                f"Aquesta bretxa s'explica per tres factors: "
                f"<strong>(i) intensitat de capital</strong> "
                f"(equips TIC i articles d'us domestic operen amb molts metres quadrats de magatzem "
                f"automatitzat per ocupat); "
                f"<strong>(ii) tícket mitjà</strong> "
                f"(un sofà o una rentadora tenen marges absoluts molt superiors a una camisa); "
                f"<strong>(iii) escala empresarial</strong> "
                f"(els subsectors amb operadors grans negocien amb proveïdors i optimitzen costos). "
                f"<br><br>"
                f"<strong>Intensitat laboral:</strong> <strong>{most_labor['label']}</strong> és el "
                f"subsector amb més persones ocupades per milió de € facturats "
                f"({most_labor['intensitat_laboral']:.1f}".replace(".", ",")
                + f" ocupats/M€), reflectint la importància de l'atenció al client en aquest segment. "
                f"<strong>{least_labor['label']}</strong> és el menys intensiu "
                f"({least_labor['intensitat_laboral']:.1f}".replace(".", ",")
                + f" ocupats/M€). "
                + (f"<br><br><strong>Dimensió empresarial mitjana:</strong> les empreses de "
                   f"<strong>{biggest['label']}</strong> facturen "
                   f"<strong>{biggest['xn_per_empresa']/1e6:.1f} M€</strong>".replace(".", ",")
                   + f" de mitjana cada una, mentre que les de <strong>{smallest['label']}</strong> "
                   f"només facturen {smallest['xn_per_empresa']/1e6:.2f} M€".replace(".", ",")
                   + ". Aquesta diferència de més de "
                   f"<strong>{biggest['xn_per_empresa']/smallest['xn_per_empresa']:.0f}× </strong>"
                   f"il·lustra la dualitat estructural del sector: pocs operadors grans en alguns "
                   f"subsectors versus xarxes molt fragmentades de petits comerços en altres."
                   if biggest is not None else "")
            )
            insight(txt)
        else:
            txt = (
                f"<strong>{top_xn['label']}</strong> domina la facturación del comercio al detalle "
                f"español con <strong>{top_xn['xifra_negoci']/1e9:.1f} k millones €</strong>".replace(".", ",")
                + f" — un <strong>{fpct(share_top_xn, 1, sign=False)}</strong> del total. "
                f"Esta concentración contrasta con el ranking por número de empresas (ver pestaña "
                f"Estructura empresarial): hay pocos operadores muy grandes (Mercadona, Carrefour, "
                f"El Corte Inglés, Lidl) que mueven el grueso del volumen. "
                f"<br><br>"
                f"<strong>Dispersión de la productividad:</strong> "
                f"<strong>{top_pr['label']}</strong> ({top_pr['productivitat']/1000:.1f}k€".replace(".", ",")
                + f" de VA por ocupado) genera "
                f"<strong>{ratio_pr:.1f}".replace(".", ",")
                + f" veces más valor</strong> por persona que <strong>{bot_pr['label']}</strong> "
                f"({bot_pr['productivitat']/1000:.1f}k€)".replace(".", ",") + ". "
                f"Esta brecha se explica por tres factores: "
                f"<strong>(i) intensidad de capital</strong> "
                f"(equipos TIC y artículos de uso doméstico operan con muchos metros cuadrados de "
                f"almacén automatizado por ocupado); "
                f"<strong>(ii) ticket medio</strong> "
                f"(un sofá o una lavadora tienen márgenes absolutos muy superiores a una camisa); "
                f"<strong>(iii) escala empresarial</strong> "
                f"(los subsectores con operadores grandes negocian con proveedores y optimizan costes). "
                f"<br><br>"
                f"<strong>Intensidad laboral:</strong> <strong>{most_labor['label']}</strong> es el "
                f"subsector con más personas ocupadas por millón de € facturados "
                f"({most_labor['intensitat_laboral']:.1f}".replace(".", ",")
                + f" ocupados/M€), reflejando la importancia de la atención al cliente en este segmento. "
                f"<strong>{least_labor['label']}</strong> es el menos intensivo "
                f"({least_labor['intensitat_laboral']:.1f}".replace(".", ",")
                + f" ocupados/M€). "
                + (f"<br><br><strong>Dimensión empresarial media:</strong> las empresas de "
                   f"<strong>{biggest['label']}</strong> facturan "
                   f"<strong>{biggest['xn_per_empresa']/1e6:.1f} M€</strong>".replace(".", ",")
                   + f" de media cada una, mientras que las de <strong>{smallest['label']}</strong> "
                   f"solo facturan {smallest['xn_per_empresa']/1e6:.2f} M€".replace(".", ",")
                   + ". Esta diferencia de más de "
                   f"<strong>{biggest['xn_per_empresa']/smallest['xn_per_empresa']:.0f}× </strong>"
                   f"ilustra la dualidad estructural del sector: pocos operadores grandes en algunos "
                   f"subsectores versus redes muy fragmentadas de pequeños comercios en otros."
                   if biggest is not None else "")
            )
            insight(txt)

# ============================================================
# TAB 3: DEMANDA - EPF
# ============================================================
with tab3:
    if df_epf.empty:
        st.info("Sense dades disponibles." if _ca else "Sin datos disponibles.")
    else:
        last_year = int(df_epf["any"].max())
        first_year = int(df_epf["any"].min())
        retail_codis = list(COICOP_TO_CNAE.keys())

        # Filtrar nomes categories de despesa que es compren al CNAE 47
        df_last = df_epf[df_epf["any"] == last_year].copy()
        df_groups = df_last[df_last["codi_coicop"].isin(retail_codis)].copy()
        # Etiquetes alineades amb els subsectors CNAE de les altres pestanyes
        df_groups["label"] = df_groups["codi_coicop"].map(DLABEL)
        df_groups["label_demanda"] = df_groups["codi_coicop"].map(CLABEL)
        df_groups["cnae_codis"] = df_groups["codi_coicop"].map(
            lambda c: ", ".join(COICOP_TO_CNAE.get(c, []))
        )
        df_groups["examples"] = df_groups["codi_coicop"].map(
            lambda c: wrap_text(", ".join(
                SUBSECTOR_EXAMPLES[LANG].get(cnae, "") for cnae in COICOP_TO_CNAE.get(c, [])
            ).strip(", "))
        )

        if _ca:
            st.caption(
                "Es mostren només les categories de despesa de les llars que es compren al "
                "**comerç al detall (CNAE 47)**. Es deixen fora les categories que no es compren "
                "al comerç minorista (habitatge, transport, restauració, educació). Les etiquetes "
                "utilitzen el mateix nom de subsector que les pestanyes Estructura empresarial i "
                "Activitat per facilitar la lectura comparada. Veure el mapeig detallat a la pàgina "
                "Metodologia."
            )
        else:
            st.caption(
                "Se muestran solo las categorías de gasto de los hogares que se compran en el "
                "**comercio al detalle (CNAE 47)**. Se dejan fuera las categorías que no se compran "
                "en el comercio minorista (vivienda, transporte, restauración, educación). Las "
                "etiquetas utilizan el mismo nombre de subsector que las pestañas Estructura "
                "empresarial y Actividad para facilitar la lectura comparada. Ver el mapeo detallado "
                "en la página Metodología."
            )

        st.subheader(
            f"{'Despesa anual de la llar al comerç al detall' if _ca else 'Gasto anual del hogar en el comercio al detalle'} ({last_year})"
        )

        df_groups = df_groups.sort_values("despesa_per_llar", ascending=True)

        fig_epf = go.Figure()
        fig_epf.add_trace(go.Bar(
            y=df_groups["label"], x=df_groups["despesa_per_llar"],
            orientation="h",
            marker_color=PURPLE,
            text=[fnum(v) + " €" for v in df_groups["despesa_per_llar"]],
            textposition="outside",
            textfont=dict(size=11),
            customdata=df_groups[["label_demanda", "cnae_codis", "examples"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                + ("<i>Categoria de despesa:</i> " if _ca else "<i>Categoría de gasto:</i> ")
                + "%{customdata[0]}<br>"
                + ("<i>CNAE associats:</i> " if _ca else "<i>CNAE asociados:</i> ")
                + "%{customdata[1]}<br>"
                + f"<i>{HOVER_LBL_EX}:</i> "
                + "%{customdata[2]}<br>"
                + ("<b>Despesa anual</b>: " if _ca else "<b>Gasto anual</b>: ")
                + "%{x:,.0f} €<extra></extra>"
            ).replace(",", "."),
        ))
        apply_layout(fig_epf,
            xaxis_title=("Despesa mitjana anual per llar (€)" if _ca else "Gasto medio anual por hogar (€)"),
            height=max(420, len(df_groups) * 38 + 100),
            margin=dict(l=320, r=120, t=40, b=50),
            hovermode="closest",
        )
        st.plotly_chart(fig_epf, use_container_width=True)
        source("INE, Enquesta de Pressupostos Familiars, taula 75003. Càlcul propi" if _ca
               else "INE, Encuesta de Presupuestos Familiares, tabla 75003. Cálculo propio")

        # KPIs: despesa al comerc al detall vs total llar, evolucio
        df_total = df_last[df_last["codi_coicop"] == "00"]
        despesa_retail = df_groups["despesa_per_llar"].sum()
        despesa_total = df_total.iloc[0]["despesa_per_llar"] if not df_total.empty else None
        quota_retail = (despesa_retail / despesa_total * 100) if despesa_total else 0

        # Evolucio quota: comparar amb primer any disponible
        df_first_yr = df_epf[df_epf["any"] == first_year]
        d_retail_first = df_first_yr[df_first_yr["codi_coicop"].isin(retail_codis)]["despesa_per_llar"].sum()
        d_total_first = df_first_yr[df_first_yr["codi_coicop"] == "00"]["despesa_per_llar"].sum()
        quota_first = (d_retail_first / d_total_first * 100) if d_total_first else 0
        delta_quota = quota_retail - quota_first

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            f"{'Despesa al comerç al detall' if _ca else 'Gasto en el comercio al detalle'} ({last_year})",
            fnum(despesa_retail) + " €",
        )
        col2.metric(
            f"{'Despesa total / llar' if _ca else 'Gasto total / hogar'} ({last_year})",
            (fnum(despesa_total) + " €") if despesa_total else "—",
        )
        col3.metric(
            f"{'% al comerç al detall' if _ca else '% en el comercio al detalle'}",
            fpct(quota_retail, 1, sign=False),
            delta=fpct(delta_quota, 1) + (f" vs {first_year}"),
            delta_color="normal",
        )
        col4.metric(
            f"{'Categoria principal' if _ca else 'Categoría principal'}",
            df_groups.iloc[-1]["label"],
            delta=fnum(df_groups.iloc[-1]["despesa_per_llar"]) + " €/any",
            delta_color="off",
        )

        # Evolucio temporal (line chart simple amb pivot table)
        st.subheader("Evolució de la despesa al llarg del temps" if _ca else "Evolución del gasto a lo largo del tiempo")

        sel_default = ["01", "03", "05", "09"]
        sel_codis = st.multiselect(
            ("Selecciona categories" if _ca else "Selecciona categorías"),
            options=retail_codis,
            default=sel_default,
            format_func=lambda c: DLABEL.get(c, c),
            key="evo_subsectors",
        )

        if sel_codis:
            df_evo = df_epf[df_epf["codi_coicop"].isin(sel_codis)].copy()
            df_evo["categoria"] = df_evo["codi_coicop"].map(DLABEL)
            df_evo = df_evo.sort_values(["codi_coicop", "any"])

            fig_evo = go.Figure()
            for i, codi in enumerate(sel_codis):
                d = df_evo[df_evo["codi_coicop"] == codi]
                if d.empty:
                    continue
                fig_evo.add_trace(go.Scatter(
                    x=d["any"].tolist(),
                    y=d["despesa_per_llar"].tolist(),
                    mode="lines+markers",
                    name=DLABEL.get(codi, codi),
                    line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                    marker=dict(size=6),
                    hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.0f} €<extra></extra>",
                ))
            fig_evo.update_layout(
                yaxis_title=("Despesa mitjana anual per llar (€)" if _ca else "Gasto medio anual por hogar (€)"),
                height=450,
                font=dict(family="DM Sans, sans-serif", size=13),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=60, r=20, t=40, b=50),
                xaxis=dict(gridcolor="rgba(0,0,0,0.06)", zeroline=False),
                yaxis=dict(gridcolor="rgba(0,0,0,0.06)", zeroline=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                hovermode="x unified",
            )
            st.plotly_chart(fig_evo, use_container_width=True)
            source("INE, Enquesta de Pressupostos Familiars (preus constants)" if _ca
                   else "INE, Encuesta de Presupuestos Familiares (precios constantes)")

        # ── Insight Demanda (analisi profunda) ─────────────────
        df_groups_sorted = df_groups.sort_values("despesa_per_llar", ascending=False)
        cat_top = df_groups_sorted.iloc[0]
        cat_bot = df_groups_sorted.iloc[-1]

        # Categoria amb major creixement i caiguda entre first_year i last_year
        df_first_lookup = df_epf[df_epf["any"] == first_year].set_index("codi_coicop")["despesa_per_llar"]
        df_last_lookup = df_epf[df_epf["any"] == last_year].set_index("codi_coicop")["despesa_per_llar"]
        var_per_cat = []
        for c in retail_codis:
            if c in df_first_lookup.index and c in df_last_lookup.index:
                v0 = df_first_lookup[c]
                v1 = df_last_lookup[c]
                if v0 > 0:
                    var_per_cat.append({
                        "codi": c,
                        "label": DLABEL.get(c, c),
                        "var_pct": (v1 / v0 - 1) * 100,
                        "abs_diff": v1 - v0,
                    })
        df_dyn = pd.DataFrame(var_per_cat)
        cat_winner = df_dyn.sort_values("var_pct", ascending=False).iloc[0] if not df_dyn.empty else None
        cat_loser = df_dyn.sort_values("var_pct", ascending=True).iloc[0] if not df_dyn.empty else None

        if _ca:
            insight(
                f"Les llars espanyoles dediquen <strong>{fnum(despesa_retail)} €/any</strong> a categories "
                f"que es compren al comerç al detall, un <strong>{fpct(quota_retail, 1, sign=False)}</strong> "
                f"de la seva despesa total ({fnum(despesa_total) if despesa_total else '—'} €). "
                f"Aquest pes ha {('augmentat' if delta_quota >= 0 else 'disminuït')} "
                f"<strong>{fpct(abs(delta_quota), 1, sign=False)}</strong> respecte al {first_year}, "
                f"cosa que reflecteix com el comerç de proximitat compita cada cop més contra "
                f"despeses no comercialitzables (lloguer, energia, oci fora de la llar). "
                f"<br><br>"
                f"L'<strong>alimentació</strong> ({fnum(cat_top['despesa_per_llar'])} €/any) concentra "
                f"el gruix de la despesa retail per llar i és estructuralment estable per la seva naturalesa "
                f"de bé bàsic. La categoria amb més dinamisme és <strong>{cat_winner['label']}</strong> "
                f"({fpct(cat_winner['var_pct'])} entre {first_year} i {last_year}), reflectint canvis "
                f"de patrons de consum. <strong>{cat_loser['label']}</strong> mostra la pitjor evolució "
                f"({fpct(cat_loser['var_pct'])}), un senyal de pressió sobre el comerç tradicional al "
                f"qual va lligada aquesta categoria. "
                f"<br><br>"
                f"<em>Despesa de les llars vs facturació de les empreses:</em> les dades d'aquesta "
                f"pestanya recullen <strong>què compren les llars espanyoles</strong>, sigui on sigui "
                f"que ho comprin (botiga del barri, web espanyola o web estrangera). En canvi, la "
                f"pestanya Activitat recull <strong>què venen les empreses fiscalment establertes "
                f"a Espanya</strong>. La diferència entre tots dos imports és informativa: "
                f"<br><br>"
                f"&nbsp;&nbsp;&nbsp;&nbsp;• Si en una categoria <strong>la despesa de les llars creix "
                f"més ràpid que la facturació del subsector espanyol</strong> corresponent, és senyal "
                f"que part del consum se'n va a canals fora del comerç al detall espanyol: marketplaces "
                f"estrangers (Amazon, AliExpress, Temu, Shein), importacions directes, o operadors "
                f"d'altres CNAE (per exemple, telefonia es paga a operadores classificats fora del CNAE 47).<br>"
                f"&nbsp;&nbsp;&nbsp;&nbsp;• Si la facturació espanyola creix més ràpid que la despesa "
                f"de les llars, és senyal de captura de quota: el comerç espanyol està venent més a "
                f"empreses, turistes o exportant.<br>"
                f"<br>"
                f"<em>La comparació no és literal</em> (cal multiplicar la despesa per llar pel nombre "
                f"de llars i el mapeig categories↔subsectors és aproximat), però la <strong>tendència "
                f"relativa</strong> sí que és reveladora i explica part de la pèrdua de teixit "
                f"empresarial en categories molt exposades als marketplaces internacionals (moda, "
                f"electrònica, articles de la llar)."
            )
        else:
            insight(
                f"Los hogares españoles dedican <strong>{fnum(despesa_retail)} €/año</strong> a categorías "
                f"que se compran en el comercio al detalle, un <strong>{fpct(quota_retail, 1, sign=False)}</strong> "
                f"de su gasto total ({fnum(despesa_total) if despesa_total else '—'} €). "
                f"Este peso ha {('aumentado' if delta_quota >= 0 else 'disminuido')} "
                f"<strong>{fpct(abs(delta_quota), 1, sign=False)}</strong> respecto a {first_year}, "
                f"reflejando cómo el comercio de proximidad compite cada vez más contra "
                f"gastos no comercializables (alquiler, energía, ocio fuera del hogar). "
                f"<br><br>"
                f"La <strong>alimentación</strong> ({fnum(cat_top['despesa_per_llar'])} €/año) concentra "
                f"el grueso del gasto minorista por hogar y es estructuralmente estable por su naturaleza "
                f"de bien básico. La categoría más dinámica es <strong>{cat_winner['label']}</strong> "
                f"({fpct(cat_winner['var_pct'])} entre {first_year} y {last_year}), reflejando cambios "
                f"en patrones de consumo. <strong>{cat_loser['label']}</strong> muestra la peor evolución "
                f"({fpct(cat_loser['var_pct'])}), señal de presión sobre el comercio tradicional ligado "
                f"a esta categoría. "
                f"<br><br>"
                f"<em>Gasto de los hogares vs facturación de las empresas:</em> los datos de esta "
                f"pestaña recogen <strong>qué compran los hogares españoles</strong>, sea donde sea "
                f"que lo compren (tienda del barrio, web española o web extranjera). En cambio, la "
                f"pestaña Actividad recoge <strong>qué venden las empresas fiscalmente establecidas "
                f"en España</strong>. La diferencia entre ambos importes es informativa: "
                f"<br><br>"
                f"&nbsp;&nbsp;&nbsp;&nbsp;• Si en una categoría <strong>el gasto de los hogares crece "
                f"más rápido que la facturación del subsector español</strong> correspondiente, es "
                f"señal de que parte del consumo se va a canales fuera del comercio al detalle español: "
                f"marketplaces extranjeros (Amazon, AliExpress, Temu, Shein), importaciones directas, "
                f"u operadores de otros CNAE (por ejemplo, telefonía se paga a operadoras clasificadas "
                f"fuera del CNAE 47).<br>"
                f"&nbsp;&nbsp;&nbsp;&nbsp;• Si la facturación española crece más rápido que el gasto "
                f"de los hogares, es señal de captura de cuota: el comercio español está vendiendo "
                f"más a empresas, turistas o exportando.<br>"
                f"<br>"
                f"<em>La comparación no es literal</em> (hay que multiplicar el gasto por hogar por "
                f"el número de hogares y el mapeo categorías↔subsectores es aproximado), pero la "
                f"<strong>tendencia relativa</strong> sí es reveladora y explica parte de la pérdida "
                f"de tejido empresarial en categorías muy expuestas a los marketplaces internacionales "
                f"(moda, electrónica, artículos del hogar)."
            )

# ─── Descàrrega ──────────────────────────────────────────────

with st.expander("Descàrrega de dades" if _ca else "Descarga de datos"):
    if not df_dirce.empty:
        st.markdown(
            "**Estructura empresarial** (empreses per subsector — Directori Central d'Empreses)"
            if _ca else
            "**Estructura empresarial** (empresas por subsector — Directorio Central de Empresas)"
        )
        st.dataframe(df_dirce, use_container_width=True, hide_index=True)
        st.download_button(
            ("Descarregar CSV (estructura)" if _ca else "Descargar CSV (estructura)"),
            df_dirce.to_csv(index=False).encode("utf-8"),
            "subsectors_estructura.csv", "text/csv",
        )
    if not df_eas.empty:
        st.markdown(
            "**Activitat empresarial** (xifra de negoci, valor afegit, personal — Enquesta Estructural d'Empreses)"
            if _ca else
            "**Actividad empresarial** (cifra de negocios, valor añadido, personal — Encuesta Estructural de Empresas)"
        )
        st.dataframe(df_eas, use_container_width=True, hide_index=True)
        st.download_button(
            ("Descarregar CSV (activitat)" if _ca else "Descargar CSV (actividad)"),
            df_eas.to_csv(index=False).encode("utf-8"),
            "subsectors_activitat.csv", "text/csv",
        )
    if not df_epf.empty:
        st.markdown(
            "**Despesa familiar** (despesa per categoria — Enquesta de Pressupostos Familiars)"
            if _ca else
            "**Gasto familiar** (gasto por categoría — Encuesta de Presupuestos Familiares)"
        )
        st.dataframe(df_epf, use_container_width=True, hide_index=True)
        st.download_button(
            ("Descarregar CSV (despesa)" if _ca else "Descargar CSV (gasto)"),
            df_epf.to_csv(index=False).encode("utf-8"),
            "subsectors_despesa.csv", "text/csv",
        )

page_meta(
    "INE: Directori Central d'Empreses (T=73019), Enquesta Estructural d'Empreses Sector Comerç (T=76818), Enquesta de Pressupostos Familiars (T=75003)"
    if _ca else
    "INE: Directorio Central de Empresas (T=73019), Encuesta Estructural de Empresas Sector Comercio (T=76818), Encuesta de Presupuestos Familiares (T=75003)",
    st.session_state.lang,
)
