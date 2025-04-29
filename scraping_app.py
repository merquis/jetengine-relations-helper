"""
Scraping Google ES → muestra 5 URLs y guarda CSV
Requiere SCRAPINGANT_KEY en secrets (10k req/mes gratis).
"""

import os, csv, urllib.parse
import streamlit as st, requests
from bs4 import BeautifulSoup
from datetime import datetime

TOP_N = 5
CSV_FILE = "urls_resultados.csv"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
API_KEY = st.secrets.get("api", {}).get("scrapingant") or os.getenv("SCRAPINGANT_KEY")

def proxy_url(url:str)->str:
    base = "https://api.scrapingant.com/v2/general"
    return f"{base}?url={urllib.parse.quote_plus(url)}&x-api-key={API_KEY}&browser=false&country=es"

def buscar(keyword:str)->list[str]:
    if not API_KEY:
        st.error("SCRAPINGANT_KEY no encontrado.")
        return []
    g_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(keyword)}&num={TOP_N}&hl=es"
    r = requests.get(proxy_url(g_url), headers={"User-Agent": USER_AGENT}, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    return [a["href"] for a in soup.select("div.yuRUbf > a")][:TOP_N]

def guardar(urls):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for u in urls:
            w.writerow([datetime.utcnow().isoformat(), u])

# ── UI ─────────────────────────────────────────────
st.set_page_config(page_title="Google Scraper", layout="wide")
st.title("🔎 Scraper Google ES (ScrapingAnt)")

kw = st.text_input("Palabra clave")
if st.button("Buscar") and kw:
    urls = buscar(kw)
    if urls:
        st.write("### Primeras 5 URLs:")
        for u in urls: st.write(u)
        guardar(urls)
        st.success(f"Guardado en {CSV_FILE}")
    else:
        st.warning("Sin resultados o bloqueo.")
