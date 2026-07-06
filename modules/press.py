"""
Recull de premsa especialitzada en comerç minorista (CNAE 47).
Agrega feeds RSS de fonts sectorials, generalistes i institucionals.

Estrategia:
- Sectorials (Distribucion Actualidad, Modaes, Alimarket): tot el contingut s'inclou.
- Generalistes i institucionals (Cinco Dias, INE, Idescat): filtre per paraules clau.
- Agregadors (Google News): consultes ja focalitzades en l'eix retail/consum.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import feedparser
import pandas as pd
import requests


# (id, nom, url, area, tipus, requereix_filtre, segment)
# Segments per a la regla de diversitat del Bloc 2:
#   gran_distribucio   — operadors d'escala nacional (cadenes, grans superfícies)
#   petit_comerc       — comerç de proximitat, petit i mitjà comerç, comerç urbà
#   centres_comercials — centres comercials, retail parks, espais comercials col·lectius
#   institucional      — organismes públics, estadística oficial
#   macro              — bancs centrals, política monetària, indicadors macro
#   general            — fonts generalistes o multisegment sense assignació clara
FEEDS = [
    ("distribucion_actualidad",
     "Distribución Actualidad",
     "https://www.distribucionactualidad.com/feed/",
     "multisector", "sectorial", False, "gran_distribucio"),

    ("diffusion_sport",
     "Diffusion Sport — Punt de venda",
     "https://www.diffusionsport.com/punto-de-venta/feed/",
     "multisector", "sectorial", False, "gran_distribucio"),

    # Feed global de Diffusion Sport (sector esports). Filtrem per
    # KEYWORDS perquè inclou també producte/marques pures sense angle
    # retail; volem només notícies amb operativa de venda.
    ("diffusion_sport_global",
     "Diffusion Sport — Global",
     "https://www.diffusionsport.com/feed/",
     "multisector", "sectorial", True, "gran_distribucio"),

    # ── Fonts RETIRADES per reserva de mineria de dades / IA (2026-05-27) ──
    # Aquests editors reserven expressament l'extracció i el tractament
    # automatitzat del seu contingut (art. 67.3 RDL 24/2021) o el prohibeixen a
    # les condicions d'ús, així que NO els ingerim per evitar problemes:
    #   · Expansión (Unidad Editorial) — política de mineria de dades explícita.
    #   · La Vanguardia (Grupo Godó) — avís legal: cita art. 67.3 + IA/minería.
    #   · Alimarket — condicions amb reserva TDM explícita + servei B2B de pagament.
    #   · Cinco Días (PRISA) — bloqueja la lectura automàtica; tractada com a restrictiva.
    # Tots quatre són també a _COVERED_DOMAINS, de manera que tampoc afloren via
    # google_retail. La cobertura es manté amb DA, Diffusion Sport, fonts públiques
    # (INE/Idescat/CCAM) i Google News (El Economista, Viaempresa, consulta retail).

    ("ine",
     "INE — Notes de premsa",
     "https://www.ine.es/dyngs/Prensa/es/rssNovedades.xml",
     "institucional", "institucional", True, "institucional"),
    ("idescat",
     "Idescat — Novetats",
     "https://www.idescat.cat/novetats/?m=rss",
     "institucional", "institucional", True, "institucional"),
    ("ccam_gencat",
     "CCAM — Consorci de Comerç, Artesania i Moda (Generalitat)",
     "https://ccam.gencat.cat/ca/actualitat/rss/index.html",
     "institucional", "institucional", False, "institucional"),

    # ── Associacions del sector (2026-06-12) ──
    # ANGED i APRESCO tenen RSS directe (verificat 200). AGECU i ANCECO bloquegen
    # el bot (403) i s'ingereixen via Google News: AGECU per site: (blog actiu de
    # comerç urbà, filtrat per keywords); ANCECO per nom (sense RSS, baix volum).
    # Filtrem amb keywords els que poden portar contingut corporatiu no-retail.
    ("anged",
     "ANGED — Grans empreses de distribució",
     "https://anged.es/feed/",
     "multisector", "sectorial", True, "gran_distribucio"),
    ("apresco",
     "APRESCO — Propietaris d'espais comercials",
     "https://www.apresco.es/feed/",
     "multisector", "sectorial", True, "centres_comercials"),
    ("google_agecu",
     "AGECU — Gerència de centres urbans (via Google News)",
     "https://news.google.com/rss/search?q=site%3Aagecu.es&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "sectorial", True, "petit_comerc"),
    ("google_anceco",
     "ANCECO — Centrals de compra (via Google News)",
     "https://news.google.com/rss/search?"
     "q=%22ANCECO%22+(%22centrales+de+compra%22+OR+%22central+de+compras%22)"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "sectorial", False, "petit_comerc"),

    # ── Fonts noves 2026-06-15 ──
    # CEC: Confederación Española de Comercio, representant del comerç urbà i de
    # proximitat d'Espanya. RSS verificat actiu (cec-comercio.org/feed/). Baix volum
    # (última entrada set-2025); filtrem amb keywords per evitar contingut corporatiu
    # no-retail. URL correcta: cec-comercio.org (cec.es i cec-comercio.es apunten a
    # entitats no relacionades: empleadors de La Corunya i un portal d'empreses).
    ("cec",
     "CEC — Confederación Española de Comercio",
     "https://cec-comercio.org/feed/",
     "multisector", "sectorial", True, "petit_comerc"),

    # ACES (Asociación Española de Centros y Parques Comerciales): no té RSS directe
    # accessible. Cobertura via Google News: cerca específica per ACES + centres
    # comercials. aces.es i acescentroscomerciales.es no resolen a feeds vàlids
    # (l'anterior és l'Associació Catalana d'Entitats de Salut). ROADMAP: verificar
    # domini oficial ACES i afegir feed directe quan estigui disponible.
    ("google_aces",
     "ACES — Centres Comercials (via Google News)",
     "https://news.google.com/rss/search?"
     "q=%22ACES%22+(%22centros+comerciales%22+OR+%22centros+y+parques+comerciales%22+"
     "OR+%22retail+park%22+OR+%22parque+comercial%22)"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "sectorial", True, "centres_comercials"),

    # ── Fonts macro: BCE i política monetària (afegit 2026-06-16) ──────────────
    # El BCE i el Banco de España generen fets que afecten directament el consum
    # minorista (tipos de interès, inflació, crèdit al consum). Cap dels feeds
    # sectorials/generalistes actuals els capta de manera fiable: el Google News
    # retail exigeix paraules retail que sovint falten als comunicats oficials; i
    # la cobertura mediàtica arriba fragmentada i tard.
    #
    # requereix_filtre=False: els feeds/queries ja estan pre-filtrats temàticament;
    # aplicar KEYWORDS (retail) descartaria precisament el que volem capturar.
    # ANTI_HARD no s'aplica (lín. 487: "if needs_filter and ..."), però ECB/BdE
    # no publiquen alertes sanitàries ni notícies de defensa, de manera que
    # ometre ANTI_HARD no genera falsos positius en la pràctica.
    #
    # ECB Statistical Press Releases: estadística d'interès (tipus d'interès
    # bancaris, agregats monetaris M3, actes del Consell de Govern). Feed RSS XML
    # actiu (verificat 2026-06-16, HTTP 200, 3 entrades recents confirmades per
    # WebFetch). En anglès; el model pot interpretar el context sense traducció.
    ("ecb_statpress",
     "ECB — Statistical Press Releases",
     "https://www.ecb.europa.eu/rss/statpress.html",
     "macro", "institucional", False, "macro"),

    # Google News BCE/macro en castellà: cobertura mediàtica espanyola de les
    # decisions del BCE i del Banco de España (Banco de España: RSS bde.es trencada
    # verificat 2026-06-16, tot el domini redirigeix a app.bde.es → 404).
    # La cerca sense filtre retail captura notícies com "El BCE sube tipos al 2,25%"
    # que els feeds generalistes filtrats per retail no detecten.
    ("google_bce_macro",
     "BCE / Política monetaria — impacte consum (via Google News)",
     "https://news.google.com/rss/search?"
     "q=(BCE+OR+%22Banco+Central+Europeo%22+OR+%22tipos+de+inter%C3%A9s%22+"
     "OR+%22pol%C3%ADtica+monetaria%22+OR+eur%C3%ADbor+OR+%22Banco+de+Espa%C3%B1a%22)"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "macro", "institucional", False, "macro"),

    # Comerç Barcelona (Consorci de Comerç de Barcelona / Ajuntament de Barcelona):
    # no té RSS directe verificat al domini comerc.barcelona. Cobertura via
    # Google News. ROADMAP: verificar comerc.barcelona/feed/ i afegir feed directe.
    ("google_comerc_barcelona",
     "Comerç Barcelona (via Google News)",
     "https://news.google.com/rss/search?"
     "q=(site%3Acomerc.barcelona+OR+%22Consorci+de+Comer%C3%A7%22+"
     "OR+%22comer%C3%A7+de+Barcelona%22+OR+%22comer%C3%A7+urbà+Barcelona%22)"
     "&hl=ca&gl=ES&ceid=ES:ca",
     "multisector", "institucional", True, "petit_comerc"),

    # Comertia (Associació de Franquícia i Retail Catalunya):
    # no té RSS directe verificat al domini comertia.com. Cobertura via
    # Google News. ROADMAP: verificar comertia.com/feed/ i afegir feed directe.
    ("google_comertia",
     "Comertia — Franquícia i Retail Catalunya (via Google News)",
     "https://news.google.com/rss/search?"
     "q=(site%3Acomertia.com+OR+%22Comertia%22+"
     "OR+%22franqu%C3%ADcia+Catalunya%22+OR+%22retail+català%22)"
     "&hl=ca&gl=ES&ceid=ES:ca",
     "multisector", "sectorial", True, "petit_comerc"),

    # Google News com a substitut de feeds amb anti-bot (Modaes, El Economista,
    # Viaempresa). Tots filtren per KEYWORDS i ANTI_KEYWORDS per evitar drift
    # cap a temàtiques no-retail (energia, agro, etc.).
    ("google_retail",
     "Google News — Retail Espanya",
     "https://news.google.com/rss/search?"
     "q=%22comercio+minorista%22+OR+%22comer%C3%A7+al+detall%22+OR+%22retail+Espa%C3%B1a%22+OR+%22distribuci%C3%B3n+comercial%22"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "agregador", True, "general"),
    # Modaes: omes. El feed directe te anti-bot i Google News no
    # indexa els titulars (retorna nomes "- Modaes" buit). La cobertura
    # de moda es manté via Alimarket non-food, Diffusion Sport i la
    # consulta general Google News retail.
    ("google_economista",
     "El Economista (via Google News)",
     "https://news.google.com/rss/search?"
     "q=site%3Aeleconomista.es+(%22comercio+minorista%22+OR+retail+OR+%22distribuci%C3%B3n+comercial%22+OR+supermercados+OR+tiendas+OR+%22gran+consumo%22)"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "generalista", True, "general"),
    ("google_viaempresa",
     "Viaempresa (via Google News)",
     "https://news.google.com/rss/search?"
     "q=site%3Aviaempresa.cat+(comer%C3%A7+OR+retail+OR+minorista+OR+distribuci%C3%B3+OR+consum+OR+botiga+OR+supermercat)"
     "&hl=ca&gl=ES&ceid=ES:ca",
     "multisector", "generalista", True, "general"),

    ("google_inforetail",
     "InfoRetail (via Google News)",
     "https://news.google.com/rss/search?q=site%3Ainforetail.es&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "sectorial", False, "general"),

    # Preferente RETIRAT (2026-06-12): és premsa turística/hotelera; les seves
    # notícies no aporten valor al resum de comerç al detall. Es manté
    # preferente.com a _COVERED_DOMAINS perquè tampoc aflori via google_retail.

    ("google_elconfidencial",
     "El Confidencial — Economia (via Google News)",
     "https://news.google.com/rss/search?q=site%3Aelconfidencial.com+(%22comercio+minorista%22+OR+retail+OR+supermercado+OR+%22gran+consumo%22+OR+%22distribuci%C3%B3n+comercial%22)&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "generalista", True, "general"),
]


KEYWORDS = [
    "comercio", "comerç", "retail", "minorista", "distribuc",
    "consum", "consumo", "tienda", "botiga",
    "supermercado", "supermercat", "hipermercado", "hipermercat",
    "ecommerce", "e-commerce", "comercio electr", "comerç electr",
    "venta", "vendes", "consumidor",
    "moda", "textil", "tèxtil", "calzado", "calçat",
    "alimentación", "alimentació",
    "centro comercial", "centre comercial",
    "cnae 47", "g-i",
]
_KW_RE = re.compile("|".join(re.escape(k) for k in KEYWORDS), re.IGNORECASE)

# Termes que sovint apareixen en notícies NO retail (energia industrial,
# agroalimentari primari, mineria) i tendeixen a colar-se via "venta" / "consumo".
# Si una notícia toca aquests temes, exigim ≥2 hits de keywords retail per
# considerar-la realment del sector — així una notícia legítima retail amb
# menció lateral a l'energia segueix passant.
ANTI_KEYWORDS = [
    "energía eléctrica", "energia elèctrica",
    "energía renovable", "energia renovable",
    "fotovoltaic", "fotovoltáic",
    "eólic", "eólica", "eòlic", "eòlica",
    "MWh", "GWh", "TWh", "kWh", "PPA",
    "Grenergy", "Iberdrola", "Endesa", "Naturgy", "Repsol",
    "agro", "agrícol", "agrari", "agricultura",
    "ramader", "ganader",
    "regadío", "regadiu", "regadiu",
    "minería", "mineria",
    "petróleo", "petroli",
    "gas natural",
    "combustible", "combustibles",
    "fósil", "fòssil", "fossil",
    "litio", "liti",
    "campo aragonés", "campo andaluz", "campo extremeño",
]
_ANTI_RE = re.compile("|".join(re.escape(k) for k in ANTI_KEYWORDS), re.IGNORECASE)

# Anti-keywords HARD: si una notícia hi toca, es descarta sempre
# (independentment de quants hits retail tingui). Per a casos on
# tot el contingut és no-retail i exigir "≥2 hits retail" no
# discrimina prou. Afegit 2026-05-21.
ANTI_KEYWORDS_HARD = [
    # Seguretat alimentària / alertes sanitàries
    "E.coli", "E. coli", "escherichia coli",
    "listeria", "salmonella", "salmonelosis",
    "alerta sanitaria", "alerta sanitària",
    "alerta alimentaria", "alerta alimentària",
    "retira lote", "retirada de lote", "retirada del lote",
    "retira partida", "retira producto", "retirada del producto",
    # Begudes espirituoses / fabricants majoristes globals (G46, no G47)
    "Diageo", "Pernod Ricard",
    "Johnnie Walker", "Jack Daniel", "Smirnoff", "Bacardi",
    "Anheuser-Busch", "AB InBev",
    "destilería", "destil·leria", "destileria",
    # Regulació immobiliària / lloguer (paraula "consum" sovint refereix
    # al Departament de Consum, no al sector minorista)
    "cláusulas abusivas", "clàusules abusives",
    "ley de vivienda", "llei d'habitatge", "llei de l'habitatge",
    "alquiler vivienda", "lloguer d'habitatge", "lloguer habitatge",
    "inmobiliaria abusiva", "immobiliària abusiva",
    # Geopolítica / defensa / conflictes bèl·lics: es colen via "venta"/"consumo"
    # (p.ex. "veta la venta de cazas a España"). Afegit 2026-05-25.
    "cazas", "caza militar", "avión de combate", "aviones de combate",
    "armamento", "armament", "armamentístic", "misil", "misiles", "míssil",
    "fuerzas armadas", "forces armades", "OTAN", "Pentágono",
    "bélico", "bélica", "bèl·lic", "bèl·lica",
    "guerra de Irán", "Irán", "Irak",
]
_ANTI_HARD_RE = re.compile("|".join(re.escape(k) for k in ANTI_KEYWORDS_HARD), re.IGNORECASE)

# Conflicte laboral / RRHH: si una notícia parla únicament d'això (sense
# operativa retail concreta), la descartem encara que mencioni una empresa
# retail. Decisió J3B3 2026-05-21: el recull és sectorial, no laboral.
LABOR_KEYWORDS = [
    "ERE", "ERTE", "expediente de regulación", "expedient de regulació",
    "sindicato", "sindicat", "sindicatos", "sindicats",
    "huelga", "vaga",
    "convenio colectivo", "conveni col·lectiu", "conveni colectiu",
    "despido", "acomiadament", "despidos", "acomiadaments",
    "comité de empresa", "comitè d'empresa",
    "movilización", "mobilització",
    "trabajadores movilizados", "treballadors mobilitzats",
    "salarios", "salaris",
]
_LABOR_RE = re.compile("|".join(re.escape(k) for k in LABOR_KEYWORDS), re.IGNORECASE)

# Termes que indiquen que la notícia parla d'operativa retail concreta
# (vendes, obertures, expansió, e-commerce, M&A). Si una notícia toca
# LABOR_KEYWORDS però cap d'aquests, no és una notícia retail útil.
RETAIL_OPS_KEYWORDS = [
    "ventas", "vendes",
    "facturación", "facturació",
    "ingresos", "ingressos",
    "beneficio", "benefici",
    "margen", "marge",
    "tienda", "tiendas", "botiga", "botigues",
    "apertura", "obertura", "aperturas", "obertures",
    "cierre de tiendas", "tancament de botigues", "cierre tiendas",
    "expansión", "expansió",
    "ecommerce", "e-commerce", "comercio electr", "comerç electr",
    "online", "en línea", "en línia",
    "fusión", "fusió", "adquisición", "adquisició",
    "OPA", "compra de", "venta de",
    "facturó", "facturà",
    "cuota de mercado", "quota de mercat",
    "nuevo formato", "nou format", "nuevo concepto", "nou concepte",
    "logística", "logística",
    "centro logístico", "centre logístic",
    "private label", "marca blanca", "marca pròpia", "marca propia",
    "consumidor", "consumidors", "consumidores",
    "consumo", "consum",
    "precio", "preu", "precios", "preus",
    "inflación", "inflació",
]
_RETAIL_OPS_RE = re.compile("|".join(re.escape(k) for k in RETAIL_OPS_KEYWORDS), re.IGNORECASE)

# Geografia: l'observatori és del comerç a Espanya. Google News retorna
# sovint mitjans llatinoamericans en castellà (mercat mexicà, colombià...).
# Si una notícia toca un país/cadena estrangera i NO menciona Espanya ni
# cap empresa retail espanyola, la descartem. Així "Inditex obre a Mèxic"
# (que SÍ interessa) es manté, però "Soriana lidera el retail mexicano" cau.
# Decisió J3B3 2026-05-22.
FOREIGN_KEYWORDS = [
    # Països i gentilicis (evitem mots ambigus com "Chile"/"Lima" en solitari)
    "México", "Mexico", "mexicano", "mexicana", "mexicanos",
    "Colombia", "colombiano", "colombiana",
    "argentino", "argentina ", "Buenos Aires",
    "chileno", "chilena", "Santiago de Chile",
    "peruano", "peruana", "Perú",
    "venezolano", "venezolana", "Venezuela",
    "ecuatoriano", "Ecuador",
    "boliviano", "Bolivia",
    "uruguayo", "Uruguay", "paraguayo", "Paraguay",
    "guatemalteco", "Guatemala", "hondureño", "Honduras",
    "Nicaragua", "Costa Rica", "Panamá", "República Dominicana",
    "Ciudad de México", "CDMX", "Guadalajara", "Monterrey",
    "Bogotá", "Medellín",
    # Cadenes de distribució no espanyoles (LATAM/altres)
    "Soriana", "Liverpool", "Falabella", "Cencosud", "Coppel",
    "Oxxo", "OXXO", "Chedraui", "Ripley", "Sodimac",
    "Walmart de México", "Walmart México", "Bodega Aurrera",
    "Grupo Éxito", "Cencosud",
]
_FOREIGN_RE = re.compile("|".join(re.escape(k) for k in FOREIGN_KEYWORDS), re.IGNORECASE)

# Senyals d'Espanya: si una notícia toca un país estranger PERÒ també
# Espanya o una empresa retail espanyola, es considera rellevant (expansió,
# comparativa, etc.) i no es descarta pel filtre geogràfic.
SPAIN_KEYWORDS = [
    "España", "español", "española", "españoles", "espanyol", "espanyola",
    "Espanya", "INE", "CNMC", "Idescat",
    # Comunitats i ciutats principals
    "Madrid", "Barcelona", "València", "Valencia", "Sevilla", "Bilbao",
    "Zaragoza", "Málaga", "Cataluña", "Catalunya", "Andalucía", "Galicia",
    "País Vasco", "Euskadi", "Comunidad Valenciana",
    # Empreses retail espanyoles
    "Mercadona", "Inditex", "Zara", "Pull&Bear", "Bershka",
    "Massimo Dutti", "Stradivarius", "El Corte Inglés", "Corte Inglés",
    "Mango", "Dia ", "Eroski", "Alcampo", "Caprabo",
    "Bonpreu", "Esclat", "Tendam", "Cortefiel", "Springfield",
    "Desigual", "Tous", "Camper", "Decathlon España", "Lidl España",
    "Carrefour España",
]
_SPAIN_RE = re.compile("|".join(re.escape(k) for k in SPAIN_KEYWORDS), re.IGNORECASE)

_UA = ("Mozilla/5.0 (compatible; ObservatoriComercBot/1.0; "
       "+https://observatori-comerc.streamlit.app)")


def _parse_date(entry):
    for k in ("published", "updated", "pubDate"):
        v = entry.get(k)
        if v:
            try:
                return parsedate_to_datetime(v)
            except Exception:
                pass
    for k in ("published_parsed", "updated_parsed"):
        v = entry.get(k)
        if v:
            try:
                return datetime(*v[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _clean_snippet(text, n=240):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    # Elimina el peu boilerplate dels feeds WordPress/Yoast que s'arrossega al
    # summary: "The post <títol> appeared first on <lloc>. <tagline>…" i
    # l'equivalent castellà "La entrada <títol> se publicó primero en <lloc>…".
    # Sempre és al final; s'elimina des d'aquí fins al final (inclou el tagline).
    text = re.sub(
        r"\s*(?:The post\b.*?\bappeared first on\b"
        r"|La entrada\b.*?\bse public[oó] primero en\b).*$",
        "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:n] + "…") if len(text) > n else text


def _matches_keywords(titol, snippet, feed_id=""):
    blob = f"{titol} {snippet}"
    # Anti-keywords HARD: descartar sempre (G46 majoristes globals,
    # alertes sanitàries, regulació immobiliària/lloguer, geopolítica/defensa...).
    if _ANTI_HARD_RE.search(blob):
        return False
    hits = _KW_RE.findall(blob)
    if not hits:
        return False
    # Agregador obert (google_retail): la consulta genèrica de Google News
    # arrossega molt contingut en castellà de LATAM, on la foraneïtat és a la
    # FONT i no al text (p.ex. mitjans argentins). Per a aquest feed exigim un
    # senyal explícit d'Espanya. Afegit 2026-05-25.
    if feed_id == "google_retail" and not _SPAIN_RE.search(blob):
        return False
    # Geografia: notícia d'un país estranger (LATAM, etc.) sense cap menció
    # a Espanya ni a una empresa retail espanyola → fora (l'observatori és
    # del comerç espanyol). "Inditex obre a Mèxic" es manté; "Soriana al
    # mercat mexicà" cau. Decisió J3B3 2026-05-22.
    if _FOREIGN_RE.search(blob) and not _SPAIN_RE.search(blob):
        return False
    # Conflicte laboral pur: si toca termes laborals (ERE, sindicat, vaga...)
    # i NO toca operativa retail concreta (vendes, botigues, expansió...),
    # descartar encara que la notícia mencioni una empresa retail per nom.
    # Decisió J3B3 2026-05-21: el recull és sectorial, no laboral.
    if _LABOR_RE.search(blob) and not _RETAIL_OPS_RE.search(blob):
        return False
    # Si la notícia toca un domini no-retail (energia, agro, mineria...) exigim
    # almenys 2 matches retail diferents per evitar falsos positius via "venta".
    if _ANTI_RE.search(blob):
        return len({h.lower() for h in hits}) >= 2
    return True


# Dominis que NO volem que aflorin a l'agregador obert (google_retail), per dos
# motius: (a) ja els cobrim per una altra via (feed directe o query dedicada) i
# evitem duplicats amb data de descoberta de Google; o (b) són editors amb reserva
# de mineria de dades que hem retirat expressament i no han d'entrar per cap porta.
_COVERED_DOMAINS = (
    # (a) coberts per una altra via
    "distribucionactualidad.com", "wpcomstaging.com",  # DA (+ mirall staging)
    "diffusionsport.com",
    "ine.es", "idescat.cat", "gencat.cat",
    "eleconomista.es",  # via google_economista
    "viaempresa.cat",   # via google_viaempresa
    # (b) editors retirats per reserva de mineria de dades (no reintroduir)
    "expansion.com", "lavanguardia.com", "cincodias.elpais.com", "elpais.com", "alimarket.es",
    "inforetail.es",      # via google_inforetail
    "preferente.com",     # suprimit (premsa turística, no aporta valor; 2026-06-12)
    "elconfidencial.com", # via google_elconfidencial
    "anged.es",           # feed directe propi
    "apresco.es",         # feed directe propi
    "agecu.es",           # via google_agecu
    "anceco.com",         # via google_anceco
    "cec-comercio.org",   # feed directe propi
)
# Google News posa la font com a sufix del títol: "Titular - domini.com".
_TITLE_SRC_RE = re.compile(r"\s[-–]\s([\w.\-]+\.\w{2,})\s*$")


def _entry_domain(entry, titol):
    """Domini d'origen d'un ítem de Google News. Google l'exposa a
    entry.source.href i també com a sufix del títol. Retorna el domini en
    minúscules (sense 'www.') o '' si no es pot determinar."""
    src = entry.get("source")
    if isinstance(src, dict):
        href = src.get("href") or src.get("url") or ""
        net = urlparse(href).netloc.lower()
        if net:
            return net[4:] if net.startswith("www.") else net
    m = _TITLE_SRC_RE.search(titol or "")
    return m.group(1).lower() if m else ""


# Fonts que mantenim però mostrant NOMÉS titular + enllaç (sense fragment), per
# prudència davant polítiques editorials restrictives. Buit ara mateix (Expansión
# s'ha tret del tot). Afegir-hi dominis —p.ex. "exemple.com"— per a futures fonts
# RSS que vulguem ser especialment conservadors a l'hora de reproduir-ne text.
_NO_SNIPPET_DOMAINS = set()


def _source_domain(entry, titol, link):
    """Domini de la font real, tant si ve de feed directe com de Google News."""
    d = _entry_domain(entry, titol)
    if d:
        return d
    net = urlparse(link or "").netloc.lower()
    return net[4:] if net.startswith("www.") else net


def _fetch_one(feed_cfg):
    feed_id, nom, url, area, tipus, needs_filter, segment = feed_cfg
    try:
        parsed = feedparser.parse(url, request_headers={"User-Agent": _UA})
    except Exception:
        return []

    rows = []
    for e in parsed.entries[:60]:
        titol = (e.get("title") or "").strip()
        snippet = _clean_snippet(e.get("summary") or e.get("description") or "")
        link = e.get("link") or ""
        if not titol or not link:
            continue
        if feed_id == "google_retail":
            dom = _entry_domain(e, titol)
            if dom and any(c in dom for c in _COVERED_DOMAINS):
                continue
        if needs_filter and not _matches_keywords(titol, snippet, feed_id):
            continue
        if _NO_SNIPPET_DOMAINS:
            _d = _source_domain(e, titol, link)
            if any(c in _d for c in _NO_SNIPPET_DOMAINS):
                snippet = ""
        rows.append({
            "data": _parse_date(e),
            "font": nom,
            "font_id": feed_id,
            "area": area,
            "tipus": tipus,
            "segment": segment,
            "titol": titol,
            "snippet": snippet,
            "link": link,
        })
    return rows


def fetch_press():
    """
    Recupera totes les entrades de tots els feeds.
    Cada feed que falli es salta silenciosament; sempre torna un DataFrame valid.
    """
    rows = []
    for f in FEEDS:
        rows.extend(_fetch_one(f))

    cols = ["data", "font", "font_id", "area", "tipus", "segment", "titol", "snippet", "link"]
    if not rows:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["link"])
    df["data"] = pd.to_datetime(df["data"], utc=True, errors="coerce")

    # Dedup entre feeds per títol normalitzat: una mateixa notícia pot arribar
    # pel feed directe de l'editor (data fiable) i per un agregador (Google News,
    # que reasigna sovint una data de descoberta recent a articles antics).
    # Conservem la versió de la font més fiable: feeds directes abans que agregadors.
    _norm = (df["titol"].str.lower()
             .str.replace(_TITLE_SRC_RE, "", regex=True)            # treu sufix "- domini.com"
             .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
             .str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip())
    df = df.assign(_norm=_norm, _trust=(df["tipus"] == "agregador").astype(int))
    df = (df.sort_values(["_trust", "data"], ascending=[True, False], na_position="last")
            .drop_duplicates(subset=["_norm"], keep="first")
            .drop(columns=["_norm", "_trust"]))

    df = df.sort_values("data", ascending=False, na_position="last").reset_index(drop=True)
    df["segment"] = df["segment"].fillna("general")
    return df[cols]


# ── Resolució d'enllaços de Google News ──────────────────────────────────────
# Els feeds de Google News retornen URLs de redirecció (news.google.com/rss/
# articles/CBMi…) amb un token opac que NO es pot descodificar localment: cal una
# crida a l'API interna batchexecute de Google. Resolem-los a la URL real de
# l'editor només per als pocs enllaços que entren al butlletí final (no a tot el
# recull, que seria desenes de crides). Qualsevol error retorna l'enllaç original
# sense petar: un enllaç de Google News funciona, només és lleig.

_GNEWS_RE = re.compile(r"https://news\.google\.com/rss/articles/[A-Za-z0-9_\-]+")
# Cookies de consentiment: sense elles la pàgina de l'article és el mur de
# consentiment EU i no exposa la signatura (data-n-a-sg) que necessita l'API.
_GNEWS_COOKIES = {
    "CONSENT": "YES+cb",
    "SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg",
}


def resolve_google_news_url(url: str, timeout: int = 12) -> str:
    """Resol una URL de redirecció de Google News a la URL real de l'editor.

    Retorna la URL original si no és un enllaç de Google News o si la resolució
    falla per qualsevol motiu (xarxa, format canviat, token caducat…).
    """
    if "news.google.com/rss/articles/" not in url:
        return url
    try:
        art = url.split("/articles/", 1)[1].split("?", 1)[0]
        s = requests.Session()
        s.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        for k, v in _GNEWS_COOKIES.items():
            s.cookies.set(k, v, domain=".google.com")
        r = s.get(
            f"https://news.google.com/rss/articles/{art}?hl=en-US&gl=US&ceid=US:en",
            timeout=timeout,
        )
        sg = re.search(r'data-n-a-sg="([^"]+)"', r.text)
        ts = re.search(r'data-n-a-ts="([^"]+)"', r.text)
        aid = re.search(r'data-n-a-id="([^"]+)"', r.text)
        if not (sg and ts):
            return url
        payload = [[[
            "Fbv4je",
            json.dumps(["garturlreq",
                        [["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1,
                          None, None, None, None, None, 0, 1],
                         "X", "X", 1, [1, 1, 1], 1, 1, None, 0, 0, None, 0],
                        (aid.group(1) if aid else art), ts.group(1), sg.group(1)]),
        ]]]
        r2 = s.post(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute",
            data="f.req=" + requests.utils.quote(json.dumps(payload)),
            timeout=timeout,
            headers={"Content-Type":
                     "application/x-www-form-urlencoded;charset=UTF-8"},
        )
        m = re.search(r'\[\\"garturlres\\",\\"(.*?)\\"', r2.text)
        if not m:
            return url
        return m.group(1).encode().decode("unicode_escape")
    except Exception:
        return url


def resolve_links_in_text(text: str, timeout: int = 12) -> tuple[str, int]:
    """Substitueix totes les URLs de Google News d'un text per l'enllaç real de
    l'editor. Retorna (text_resolt, nombre d'enllaços resolts amb èxit). Cada URL
    es resol un sol cop encara que aparegui més d'una vegada.
    """
    cache: dict[str, str] = {}
    resolts = 0
    for u in dict.fromkeys(_GNEWS_RE.findall(text)):
        nou = resolve_google_news_url(u, timeout=timeout)
        cache[u] = nou
        if nou != u:
            resolts += 1
    for u, nou in cache.items():
        if nou != u:
            text = text.replace(u, nou)
    return text, resolts
