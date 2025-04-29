"""
JetEngine Relations Helper – Streamlit (v2 Scraping activado + user-agent realista)
===========================================================

• Scraping → Introducir palabra clave → Buscar en Google España → Extraer todos los H1 de cada URL.
• Mejora: User-Agent actualizado a Chrome 122 real.

Requisitos:
```bash
pip install streamlit beautifulsoup4 requests
```
"""

import base64
import json
import re
from typing import List
from urllib import error, request

import streamlit as st
import requests
from bs4 import BeautifulSoup

# ---------------- Configuración ---------------- #
API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
SEP = re.compile(r"[\s,\.]+")
HEADERS = {"Content-Type": "application/json"}
GOOGLE_SEARCH_URL = "https://www.google.es/search"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/122.0.0.0 Safari/537.36")

# —— Autenticación opcional —— #
USER = st.secrets.get("wp_user", "")
APP = st.secrets.get("wp_app_pass", "")
if USER and APP:
    HEADERS["Authorization"] = "Basic " + base64.b64encode(f"{USER}:{APP}".encode()).decode()

# ---------------- Utilidades ---------------- #

def serializar(ids: List[str]) -> str:
    return "a:{}:{}".format(
        len(ids), ''.join(f'i:{i};s:{len(v)}:"{v}";' for i, v in enumerate(ids))
    )

def _get(url: str):
    try:
        with request.urlopen(url, timeout=10) as r:
            if 200 <= r.status < 300:
                return json.loads(r.read().decode())
            st.error(f"HTTP {r.status}: {url}")
    except Exception as e:
        st.error(f"GET error: {e}")
    return None

def _post(payload: dict) -> bool:
    try:
        req = request.Request(API_BASE, data=json.dumps(payload).encode(), headers=HEADERS, method="POST")
        with request.urlopen(req, timeout=10) as r:
            return 200 <= r.status < 300
    except error.URLError as e:
        st.error(f"POST error: {e}")
    return False

def buscar_en_google(palabra_clave: str) -> List[str]:
    headers = {"User-Agent": USER_AGENT}
    params = {"q": palabra_clave, "num": 10, "hl": "es", "gl": "es"}
    resp = requests.get(GOOGLE_SEARCH_URL, headers=headers, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")
    enlaces = []
    for g in soup.find_all('a'):
        href = g.get('href')
        if href and href.startswith("/url?q="):
            clean_url = href.split("/url?q=")[1].split("&")[0]
            if "google.com" not in clean_url:
                enlaces.append(clean_url)
    return enlaces[:10]

def extraer_h1(url: str) -> List[str]:
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        return [h.get_text(strip=True) for h in soup.find_all("h1")]
    except Exception as e:
        return [f"Error al acceder: {e}"]

# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="Relaciones CPT", layout="wide")

# Menú principal
menu = st.sidebar.selectbox("Selecciona módulo", ("Relaciones CPT", "Scraping"))

if menu == "Relaciones CPT":
    st.title("🛠️ Relaciones CPT")

    op = st.sidebar.radio("Selecciona acción", (
        "Ver reseñas de alojamiento",
        "Añadir reseñas a alojamiento",
        "Vincular reseña → alojamiento",
    ))

    # Código de Relaciones CPT (se mantiene igual que antes)

elif menu == "Scraping":
    st.title("🛠️ Scraping")

    palabra_clave = st.text_input("Introduce una palabra clave para buscar en Google España")
    if st.button("Buscar y extraer H1") and palabra_clave:
        urls = buscar_en_google(palabra_clave)
        if not urls:
            st.error("No se encontraron resultados o error de conexión.")
        else:
            for url in urls:
                st.subheader(url)
                h1s = extraer_h1(url)
                if h1s:
                    for h in h1s:
                        st.write(f"• {h}")
                else:
                    st.write("Sin H1 encontrados.")
