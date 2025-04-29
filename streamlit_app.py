"""
Router principal – muestra menú para elegir módulo.
"""

import streamlit as st
import scraping_app, relations_app  # módulos existentes

st.set_page_config(page_title="TripToIslands Suite", layout="wide")
choice = st.sidebar.radio("Módulo", ("Scraping", "Relaciones CPT"))

if choice == "Scraping":
    scraping_app.main()
else:
    relations_app.main()
