"""
Scraping Google ES con ScrapingAnt (5 URLs)
"""

import os, csv, urllib.parse, requests, streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime

TOP_N = 5
CSV_FILE = "urls_resultados.csv"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/123.0.0.0 Safari/537.36")

API_KEY = st.secrets.get("api", {}).get("scrapingant") \
          or os.getenv("SCRAPINGANT_KEY")

# ---------- helpers ----------
def proxy_url(url: str) -> str:
    base = "https://api.scrapingant.com/v2/general"
    params = {"url": url, "x-api-key": API_KEY,
              "browser": "false", "country": "es"}
    return f"{base}?{urllib.parse.urlencode(params)}"

def google_search(keyword: str) -> list[str]:
    if not API_KEY:
        st.error("SCRAPINGANT_KEY no definido.")
        return []
    g_url = (
        "https://www.google.com/search?"
        f"q={urllib.parse.quote_plus(keyword)}&num={TOP_N}&hl=es"
    )
    r = requests.get(proxy_url(g_url),
                     headers={"User-Agent": USER_AGENT}, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    return [a["href"] for a in soup.select("div.yuRUbf > a")][:TOP_N]

def guardar_csv(urls: list[str]):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f); now = datetime.utcnow().isoformat()
        for u in urls:
            w.writerow([now, u])

# ---------- UI ----------
def main():
    st.set_page_config(page_title="Scraping Google", layout="wide")
    st.title("🔎 Scraper Google ES (ScrapingAnt)")

    kw = st.text_input("Palabra clave")
    if st.button("Buscar") and kw:
        urls = google_search(kw)
        if urls:
            st.subheader("Primeras 5 URLs")
            for u in urls: st.write(u)
            guardar_csv(urls)
            st.success(f"Guardado en {CSV_FILE}")
        else:
            st.warning("Sin resultados o Google bloqueado.")

if __name__ == "__main__":
    main()
