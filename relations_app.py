"""
Gestión de Relaciones CPT con JetEngine (mínimo)
"""

import base64, streamlit as st, requests

API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
HEADERS  = {"Content-Type": "application/json"}

WP_USER = st.secrets.get("wp", {}).get("user")
WP_APP  = st.secrets.get("wp", {}).get("app_pass")

if WP_USER and WP_APP:
    token = base64.b64encode(f"{WP_USER}:{WP_APP}".encode()).decode()
    HEADERS["Authorization"] = f"Basic {token}"

def main():
    st.set_page_config(page_title="Relaciones CPT", layout="wide")
    st.title("🛠️ Relaciones CPT – JetEngine")

    op = st.sidebar.radio(
        "Acción",
        ("Ver reseñas de alojamiento",
         "Añadir reseñas a alojamiento",
         "Vincular reseña → alojamiento")
    )

    st.write(f"🚧 Implementa aquí la lógica para **{op}**.")
    if st.button("Test JetEngine"):
        r = requests.get(API_BASE, headers=HEADERS, timeout=20)
        st.write("Status:", r.status_code)
        st.json(r.json() if r.ok else r.text)

if __name__ == "__main__":
    main()
