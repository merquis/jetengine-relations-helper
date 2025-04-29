"""
TripToIslands • Google Scraper vía ScrapingAnt
=============================================

• Introduce una palabra clave.
• El backend pide la SERP a Google usando ScrapingAnt (evita CAPTCHA).
• Se muestran las 5 primeras URLs orgánicas y se guardan en urls_resultados.csv
"""

import os, urllib.parse, csv, pandas as pd, streamlit as st, requests
from bs4 import BeautifulSoup
from datetime import datetime

# ── Constantes ──────────────────────────────────────────────────────
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/123.0.0.0 Safari/537.36")
TOP_N = 5
CSV_FILE = "urls_resultados.csv"

# ── Obtener API-Key desde secrets o variable entorno ────────────────
SCRAPINGANT_KEY = (
    st.secrets.get("api", {}).get("scrapingant") or
    os.getenv("SCRAPINGANT_KEY")
)

# ── Funciones utilitarias ───────────────────────────────────────────
def build_proxy_url(target_url: str) -> str:
    """Convierte cualquier URL en una llamada a ScrapingAnt."""
    base = "https://api.scrapingant.com/v2/general"
    params = {
        "x-api-key": SCRAPINGANT_KEY,
        "url": target_url,
        "browser": "false",      # HTML plano: 1 crédito
        "country": "es"
    }
    return f"{base}?{urllib.parse.urlencode(params)}"

def buscar_en_google(keyword: str) -> list[str]:
    """Devuelve las primeras TOP_N URLs orgánicas para la keyword."""
    if not SCRAPINGANT_KEY:
        st.error("⚠️ Falta SCRAPINGANT_KEY en secrets o variables de entorno.")
        return []

    query = urllib.parse.quote_plus(keyword)
    google_url = f"https://www.google.com/search?q={query}&num={TOP_N}&hl=es"
    proxy_url  = build_proxy_url(google_url)

    resp = requests.get(proxy_url, headers={"User-Agent": USER_AGENT}, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")

    links = [a["href"] for a in soup.select("div.yuRUbf > a")][:TOP_N]
    return links

def guardar_urls_en_csv(urls: list[str]):
    """Añade las URLs a un CSV con marca de tiempo."""
    new_rows = [{"keyword_time": datetime.now().isoformat(),
                 "url": u} for u in urls]

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_rows[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_rows)

# ── INTERFAZ STREAMLIT ──────────────────────────────────────────────
st.set_page_config(page_title="Google Scraper • TripToIslands", layout="wide")
st.title("🔎 Scraping Google (vía ScrapingAnt)")

keyword = st.text_input("Introduce una palabra clave (Google ES)")
if st.button("Buscar") and keyword:
    with st.spinner("Consultando Google..."):
        urls = buscar_en_google(keyword)

    if urls:
        st.success(f"Se encontraron {len(urls)} URLs:")
        for u in urls:
            st.write(f"• {u}")
        guardar_urls_en_csv(urls)
        st.info(f"Guardado/actualizado en {CSV_FILE}")
    else:
        st.warning("Google devolvió cero resultados o un bloqueo (CAPTCHA).")
