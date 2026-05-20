"""
Recull de premsa especialitzada en comerç minorista (CNAE 47).
Agrega feeds RSS de fonts sectorials, generalistes i institucionals.

Estrategia:
- Sectorials (Distribucion Actualidad, Modaes, Alimarket): tot el contingut s'inclou.
- Generalistes i institucionals (Cinco Dias, INE, Idescat): filtre per paraules clau.
- Agregadors (Google News): consultes ja focalitzades en l'eix retail/consum.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import pandas as pd


_ALIMARKET_BASE = "https://www.alimarket.es/media/rss/sectores/"

# (id, nom, url, area, tipus, requereix_filtre)
FEEDS = [
    ("distribucion_actualidad",
     "Distribución Actualidad",
     "https://www.distribucionactualidad.com/feed/",
     "multisector", "sectorial", False),

    ("diffusion_sport",
     "Diffusion Sport — Punt de venda",
     "https://www.diffusionsport.com/punto-de-venta/feed/",
     "multisector", "sectorial", False),

    ("expansion_distribucion",
     "Expansión — Distribució",
     "https://www.expansion.com/rss/empresasdistribucion.xml",
     "multisector", "sectorial", False),

    ("la_vanguardia",
     "La Vanguardia — Economia",
     "https://www.lavanguardia.com/rss/economia.xml",
     "multisector", "generalista", True),

    # Alimarket: un feed XML per sector; cada feed publica nomes l'ultim item.
    # Agreguem diversos sectors per cobrir comerç al detall en sentit ampli.
    ("alimarket_base",
     "Alimarket — Distribució base alimentària",
     _ALIMARKET_BASE + "alimentacion-distribucion-base-alimentaria.xml",
     "alimentacio", "sectorial", False),
    ("alimarket_esp",
     "Alimarket — Distribució especialitzada alimentària",
     _ALIMARKET_BASE + "alimentacion-distribucion-especializada-alimentaria-generico.xml",
     "alimentacio", "sectorial", False),
    ("alimarket_nonfood",
     "Alimarket — Distribució no alimentària",
     _ALIMARKET_BASE + "non-food-distribucion-especializada-no-alimentaria.xml",
     "multisector", "sectorial", False),
    ("alimarket_perfumeria",
     "Alimarket — Perfumeria i cosmètica",
     _ALIMARKET_BASE + "non-food-distribucion-perfumeria-cosmetica.xml",
     "multisector", "sectorial", False),
    ("alimarket_electro",
     "Alimarket — Electrodomèstics i tecnologia",
     _ALIMARKET_BASE + "electro-distribucion-generalistas-con-electro.xml",
     "multisector", "sectorial", False),

    ("cinco_dias",
     "Cinco Días",
     "https://cincodias.elpais.com/rss/cincodias/portada.xml",
     "multisector", "generalista", True),

    ("ine",
     "INE — Notes de premsa",
     "https://www.ine.es/dyngs/Prensa/es/rssNovedades.xml",
     "institucional", "institucional", True),
    ("idescat",
     "Idescat — Novetats",
     "https://www.idescat.cat/novetats/?m=rss",
     "institucional", "institucional", True),
    ("ccam_gencat",
     "CCAM — Consorci de Comerç, Artesania i Moda (Generalitat)",
     "https://ccam.gencat.cat/ca/actualitat/rss/index.html",
     "institucional", "institucional", False),

    # Google News com a substitut de feeds amb anti-bot (Modaes, El Economista,
    # Viaempresa). Tots filtren per KEYWORDS i ANTI_KEYWORDS per evitar drift
    # cap a temàtiques no-retail (energia, agro, etc.).
    ("google_retail",
     "Google News — Retail Espanya",
     "https://news.google.com/rss/search?"
     "q=%22comercio+minorista%22+OR+%22comer%C3%A7+al+detall%22+OR+%22retail+Espa%C3%B1a%22+OR+%22distribuci%C3%B3n+comercial%22"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "agregador", True),
    # Modaes: omes. El feed directe te anti-bot i Google News no
    # indexa els titulars (retorna nomes "- Modaes" buit). La cobertura
    # de moda es manté via Alimarket non-food, Diffusion Sport i la
    # consulta general Google News retail.
    ("google_economista",
     "El Economista (via Google News)",
     "https://news.google.com/rss/search?"
     "q=site%3Aeleconomista.es+(%22comercio+minorista%22+OR+retail+OR+%22distribuci%C3%B3n+comercial%22+OR+supermercados+OR+tiendas+OR+%22gran+consumo%22)"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "generalista", True),
    ("google_viaempresa",
     "Viaempresa (via Google News)",
     "https://news.google.com/rss/search?"
     "q=site%3Aviaempresa.cat+(comer%C3%A7+OR+retail+OR+minorista+OR+distribuci%C3%B3+OR+consum+OR+botiga+OR+supermercat)"
     "&hl=ca&gl=ES&ceid=ES:ca",
     "multisector", "generalista", True),
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
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:n] + "…") if len(text) > n else text


def _matches_keywords(titol, snippet):
    blob = f"{titol} {snippet}"
    hits = _KW_RE.findall(blob)
    if not hits:
        return False
    # Si la notícia toca un domini no-retail (energia, agro, mineria...) exigim
    # almenys 2 matches retail diferents per evitar falsos positius via "venta".
    if _ANTI_RE.search(blob):
        return len({h.lower() for h in hits}) >= 2
    return True


def _fetch_one(feed_cfg):
    feed_id, nom, url, area, tipus, needs_filter = feed_cfg
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
        if needs_filter and not _matches_keywords(titol, snippet):
            continue
        rows.append({
            "data": _parse_date(e),
            "font": nom,
            "font_id": feed_id,
            "area": area,
            "tipus": tipus,
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

    cols = ["data", "font", "font_id", "area", "tipus", "titol", "snippet", "link"]
    if not rows:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["link"])
    df["data"] = pd.to_datetime(df["data"], utc=True, errors="coerce")
    df = df.sort_values("data", ascending=False, na_position="last").reset_index(drop=True)
    return df[cols]
