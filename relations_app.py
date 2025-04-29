"""
JetEngine Relations Helper  ·  Streamlit
----------------------------------------
• Módulo Relaciones CPT (WordPress + JetEngine)
• Módulo Scraping (5 primeras URLs de Google España)
"""

import base64
from typing import List

import streamlit as st
import requests
from bs4 import BeautifulSoup

# ---------- Configuración WP / JetEngine ----------
API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
HEADERS  = {"Content-Type": "application/json"}

USER = st.secrets.get("wp_user")
APP  = st.secrets.get("wp_app_pass")
if USER and APP:
    token = base64.b64encode(f"{USER}:{APP}".encode()).decode()
    HEADERS["Authorization"] = f"Basic {token}"

# ---------- Configuración Scraping ----------
GOOGLE_SEARCH_URL = "https://www.google.es/search"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/123.0.0.0 Safari/537.36")

def buscar_en_google(palabra_clave: str) -> List[str]:
    headers = {"User-Agent": USER_AGENT}
    params  = {"q": palabra_clave, "hl": "es", "gl": "es", "num": 10}
    resp    = requests.get(GOOGLE_SEARCH_URL, headers=headers, params=params, timeout=15)
    if resp.status_code != 200:
        return []
    soup    = BeautifulSoup(resp.text, "html.parser")
    enlaces = []
    for div in soup.find_all('div', class_='tF2Cxc'):
        a = div.find('a', href=True)
        if a:
            enlaces.append(a['href'])
    return enlaces[:5]

# ---------- Streamlit UI ----------
st.set_page_config(page_title="TripToIslands Helper", layout="wide")

menu = st.sidebar.selectbox("Selecciona módulo", ("Relaciones CPT", "Scraping"))

# --- Relaciones CPT ---
if menu == "Relaciones CPT":
    st.title("🛠️ Relaciones CPT")
    op = st.sidebar.radio("Acción", (
        "Ver reseñas de alojamiento",
        "Añadir reseñas a alojamiento",
        "Vincular reseña → alojamiento",
    ))
    st.info(f"Implementa aquí la lógica para **{op}**.")

# --- Scraping ---
else:
    st.title("🛠️ Scraping")
    kw = st.text_input("Introduce una palabra clave (Google ES)")
    if st.button("Buscar URLs") and kw:
        urls = buscar_en_google(kw)
        if not urls:
            st.error("No se encontraron resultados o error de conexión.")
        else:
            st.subheader("Primeras 5 URLs encontradas:")
            for u in urls:
                st.write(f"- {u}")
