import base64, re, json
import streamlit as st
import requests

# ── Config WP / JetEngine ─────────────────────────────
API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
HEADERS = {"Content-Type": "application/json"}

USER = st.secrets.get("wp_user", "")
APP  = st.secrets.get("wp_app_pass", "")
if USER and APP:
    token = base64.b64encode(f"{USER}:{APP}".encode()).decode()
    HEADERS["Authorization"] = f"Basic {token}"

# ── UI ────────────────────────────────────────────────
st.set_page_config(page_title="Relaciones CPT", layout="wide")
st.title("🛠️ Relaciones CPT")

op = st.sidebar.radio(
    "Selecciona acción",
    ("Ver reseñas de alojamiento",
     "Añadir reseñas a alojamiento",
     "Vincular reseña → alojamiento")
)

st.write(f"Aquí iría la lógica para *{op}* …")
# Tu código JetEngine se queda aquí
