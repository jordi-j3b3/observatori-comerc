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

    # Google News com a substitut de feeds amb anti-bot (Modaes, El Economista)
    ("google_retail",
     "Google News — Retail Espanya",
     "https://news.google.com/rss/search?"
     "q=%22comercio+minorista%22+OR+%22comer%C3%A7+al+detall%22+OR+%22retail+Espa%C3%B1a%22+OR+%22distribuci%C3%B3n+comercial%22"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "agregador", False),
    ("google_modaes",
     "Modaes (via Google News)",
     "https://news.google.com/rss/search?"
     "q=site%3Amodaes.es"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "moda", "sectorial", False),
    ("google_economista",
     "El Economista (via Google News)",
     "https://news.google.com/rss/search?"
     "q=site%3Aeleconomista.es+(retail+OR+comercio+OR+consumo+OR+distribuci%C3%B3n)"
     "&hl=es-ES&gl=ES&ceid=ES:es",
     "multisector", "generalista", False),
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
    return bool(_KW_RE.search(blob))


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
