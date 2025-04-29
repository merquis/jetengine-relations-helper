"""
TripToIslands · Google Scraper  →  CSV  →  WordPress CPT + JetEngine Relation
============================================================================
• Busca en Google España vía ScrapingAnt (1 crédito).
• Muestra y guarda las 5 primeras URLs orgánicas (sin duplicados).
• Crea/actualiza un CPT “fuente” (o el que definas) en tu WordPress.
• Relaciona ese CPT con la reseña/alojamiento seleccionado mediante JetEngine.
"""

# ────────── Imports ──────────────────────────────────────────────────────
import os, csv, urllib.parse, hashlib, time
from dataclasses import dataclass, asdict, fields
from datetime import datetime

import streamlit as st
import requests
from bs4 import BeautifulSoup

# ────────── CONFIG ───────────────────────────────────────────────────────
TOP_N = 5
CSV_FILE = "urls_resultados.csv"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/123.0.0.0 Safari/537.36")

# ScrapingAnt API KEY  (secrets.toml o variable entorno)
SCRAPINGANT_KEY = (st.secrets.get("api", {}).get("scrapingant")
                   or os.getenv("SCRAPINGANT_KEY"))

# WordPress / JetEngine
WP_USER = st.secrets.get("wp", {}).get("user") or os.getenv("WP_USER")
WP_APP  = st.secrets.get("wp", {}).get("app_pass") or os.getenv("WP_APP_PASS")
WP_CPT_ENDPOINT = "https://triptoislands.com/wp-json/wp/v2/fuente"
JET_REL_ENDPOINT = "https://triptoislands.com/wp-json/jet-rel/12"  # id relación

HEADERS = {"Content-Type": "application/json"}
if WP_USER and WP_APP:
    import base64
    HEADERS["Authorization"] = "Basic " + base64.b64encode(
        f"{WP_USER}:{WP_APP}".encode()).decode()

# ────────── Estructuras de datos ─────────────────────────────────────────
@dataclass
class SearchData:
    keyword:       str
    title:         str
    link:          str
    result_number: int
    scraped_at:    str

    def __post_init__(self):
        for fld in fields(self):
            val = getattr(self, fld.name)
            if isinstance(val, str):
                setattr(self, fld.name, val.strip() or f"no_{fld.name}")

class DataPipeline:
    def __init__(self, csv_filename:str, queue_limit:int=50):
        self.csv_filename = csv_filename
        self.queue_limit  = queue_limit
        self.queue        = []
        self.links_seen   = set()

    def _flush(self):
        if not self.queue: return
        keys = [f.name for f in fields(self.queue[0])]
        file_exists = os.path.isfile(self.csv_filename)
        with open(self.csv_filename, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, keys)
            if not file_exists:
                w.writeheader()
            w.writerows(asdict(item) for item in self.queue)
        self.queue.clear()

    def add(self, item: SearchData):
        if item.link in self.links_seen: return
        self.links_seen.add(item.link)
        self.queue.append(item)
        if len(self.queue) >= self.queue_limit:
            self._flush()

    def close(self):
        self._flush()

# ────────── Scraping helpers ─────────────────────────────────────────────
def proxy_url(target:str)->str:
    base = "https://api.scrapingant.com/v2/general"
    params = {"url": target, "x-api-key": SCRAPINGANT_KEY,
              "browser": "false", "country": "es"}
    return f"{base}?{urllib.parse.urlencode(params)}"

def google_search(keyword:str)->list[tuple[str,str]]:
    """Devuelve lista (title, url) usando ScrapingAnt → Google ES."""
    if not SCRAPINGANT_KEY:
        st.error("SCRAPINGANT_KEY no configurada.")
        return []
    q = urllib.parse.quote_plus(keyword)
    g_url = f"https://www.google.com/search?q={q}&num={TOP_N}&hl=es"
    r = requests.get(proxy_url(g_url),
                     headers={"User-Agent": USER_AGENT}, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("div.yuRUbf > a")[:TOP_N]
    return [(a.get_text(" ", strip=True), a["href"]) for a in links]

# ────────── WordPress helpers ────────────────────────────────────────────
def wp_upsert_fuente(title:str, url:str)->int|None:
    """Crea (o recupera) CPT 'fuente' y devuelve su ID."""
    slug = hashlib.md5(url.encode()).hexdigest()[:20]
    payload = {"title": title, "status": "publish", "slug": slug,
               "acf": {"source_url": url}}
    r = requests.post(WP_CPT_ENDPOINT, headers=HEADERS, json=payload, timeout=30)
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 400 and "existing_post_id" in r.text:
        return r.json()["data"]["existing_post_id"]
    st.warning(f"WP error {r.status_code}: {r.text}")
    return None

def relate_posts(parent:int, child:int):
    payload = {"parent_id": parent, "child_id": child}
    r = requests.post(JET_REL_ENDPOINT, headers=HEADERS, json=payload, timeout=20)
    if not r.ok:
        st.error(f"Relación falló: {r.text}")

# ────────── Streamlit UI ────────────────────────────────────────────────
st.set_page_config(page_title="Google→WP Scraper", layout="wide")
st.title("🔗 Google Scrape + JetEngine Sync")

keyword = st.text_input("Palabra clave Google ES")
review_id = st.text_input("ID de reseña/alojamiento (parent CPT)", "")
run = st.button("Buscar y serializar")

if run and keyword:
    urls = google_search(keyword)
    if not urls:
        st.warning("Sin resultados.")
    else:
        pipe = DataPipeline(CSV_FILE)
        st.success(f"Mostrando y guardando {len(urls)} URLs")
        for idx,(title,url) in enumerate(urls,1):
            st.write(f"{idx}. {title} — {url}")
            pipe.add(SearchData(keyword, title, url, idx, datetime.utcnow().isoformat()))

            # --- WordPress: crear fuente + relacionar ---
            if review_id.isdigit() and WP_USER and WP_APP:
                fuente_id = wp_upsert_fuente(title, url)
                if fuente_id: relate_posts(int(review_id), fuente_id)
        pipe.close()
        st.info(f"CSV actualizado • {CSV_FILE}")
