#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JetEngine Relations Helper – Streamlit
======================================

• Sección “Relaciones CPT” — mantiene tus herramientas de reseñas/Alojamientos.  
• Sección “Scraping”       — de momento solo imprime “HOLA”.
"""

# ──────────────────────── IMPORTS ────────────────────────
import base64
import re
from typing import List

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

# ────────────────── CONFIGURACIÓN GLOBAL ─────────────────
API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
SEP = re.compile(r"[\s,\.]+")
HEADERS = {"Content-Type": "application/json"}
GOOGLE_SEARCH_URL = "https://www.google.es/search"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

# (Opcional) Autenticación si usas la API REST protegida de tu WP
USER = st.secrets.get("wp_user", "")
APP = st.secrets.get("wp_app_pass", "")
if USER and APP:
    HEADERS["Authorization"] = (
        "Basic " + base64.b64encode(f"{USER}:{APP}".encode()).decode()
    )

# ─────────────── UTILIDADES (scraping rápido) ────────────
def buscar_en_google(palabra_clave: str) -> List[str]:
    """Devuelve las 5 primeras URLs externas de Google (modo libre)."""
    headers = {"User-Agent": USER_AGENT}
    params = {"q": palabra_clave, "hl": "es", "gl": "es", "num": 10}

    resp = requests.get(GOOGLE_SEARCH_URL, headers=headers, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")

    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # /url?q=https://sitio.com&sa=...
        if href.startswith("/url?q="):
            clean = href.split("/url?q=")[1].split("&")[0]
            if "google.com" not in clean and "webcache.googleusercontent.com" not in clean:
                urls.append(clean)
        # Enlaces directos (raro, pero pueden aparecer)
        elif href.startswith("http") and "google.com" not in href:
            urls.append(href)

    return urls[:5]


def guardar_urls_en_csv(urls: List[str], filename: str = "urls_resultados.csv"):
    pd.DataFrame(urls, columns=["URL"]).to_csv(filename, index=False)


# ────────────────────── STREAMLIT UI ─────────────────────
st.set_page_config(page_title="Relaciones CPT & Scraping", layout="wide")

# ▸▸ Barra lateral – menú principal
seccion = st.sidebar.selectbox("Selecciona módulo", ("Relaciones CPT", "Scraping"))

# ╭─────────────────── 1. RELACIONES CPT ─────────────────╮
if seccion == "Relaciones CPT":
    st.title("🛠️ Relaciones CPT")

    accion = st.sidebar.radio(
        "Selecciona acción",
        (
            "Ver reseñas de alojamiento",
            "Añadir reseñas a alojamiento",
            "Vincular reseña → alojamiento",
        ),
    )

    # Aquí sigue tu lógica existente…
    # Ejemplo de placeholder:
    if accion == "Ver reseñas de alojamiento":
        st.info("Aquí iría la tabla / buscador de reseñas.")
    elif accion == "Añadir reseñas a alojamiento":
        st.info("Formulario para añadir nuevas reseñas…")
    elif accion == "Vincular reseña → alojamiento":
        st.info("Herramienta para vincular reseña ↔ alojamiento…")

# ╭──────────────────── 2. SCRAPING ───────────────────────╮
elif seccion == "Scraping":
    st.title("🛠️ Scraping")

    st.write("HOLA")  # ← De momento solo esto

    # Ejemplo: futuro cuadro de búsqueda
    # palabra = st.text_input("Palabra clave")
    # if st.button("Buscar"):
    #     urls = buscar_en_google(palabra)
    #     st.write(urls)
    #     guardar_urls_en_csv(urls)
