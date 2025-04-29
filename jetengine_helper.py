"""
JetEngine Relations Helper – Streamlit (v2.2 Scraping mejorado)
===========================================================

• Scraping → Introducir palabra clave → Buscar en Google España → Mostrar solo 5 primeras URLs (scraping actualizado).

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
              "Chrome/123.0.0.0 Safari/537.36")

# —— Autenticación opcional —— #
USER = st.secrets.get("wp_user", "")
APP = st.secrets.get("wp_app_pass", "")
if USER and APP:
    HEADERS["Authorization"] = "Basic " + base64.b64encode(f"{USER}:{APP}".encode()).decode()

# ---------------- Utilidades ---------------- #

def buscar_en_google(palabra_clave: str) -> List[str]:
    headers = {"User-Agent": USER_AGENT}
    params = {"q": palabra_clave, "hl": "es", "gl": "es", "num": 10}
    resp = requests.get(GOOGLE_SEARCH_URL, headers=headers, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")

    enlaces = []
    for div in soup.find_all('div', class_='tF2Cxc'):
        a_tag = div.find('a', href=True)
        if a_tag:
            enlaces.append(a_tag['href'])
    return enlaces[:5]

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
    if st.button("Buscar URLs") and palabra_clave:
        urls = buscar_en_google(palabra_clave)
        if not urls:
            st.error("No se encontraron resultados o error de conexión.")
        else:
            st.subheader("Primeras 5 URLs encontradas:")
            for url in urls:
                st.write(f"- {url}")
