"""
Relaciones CPT (JetEngine) – TripToIslands
-----------------------------------------

• Ver Alojamiento + sus Reseñas
• Crear nueva Reseña y vincularla
• Vincular una reseña existente

Requisitos:
pip install streamlit requests
"""

# ───────── CONFIG WP / JetEngine ────────────
import base64, json, requests, streamlit as st

SITE   = "https://triptoislands.com"
REL_ID = "12"         # ID de la relación JetEngine (padre-hijo)
CPT_REVIEW = "review" # slug CPT reseñas
CPT_HOTEL  = "hotel"  # slug CPT alojamiento

WP_USER = st.secrets.get("wp_user")
WP_APP  = st.secrets.get("wp_app_pass")

HEADERS = {"Content-Type": "application/json"}
if WP_USER and WP_APP:
    HEADERS["Authorization"] = (
        "Basic " + base64.b64encode(f"{WP_USER}:{WP_APP}".encode()).decode()
    )

# ───────── HELPER HTTP ────────────
def wp_get(endpoint, params=None):
    url = f"{SITE}/wp-json/wp/v2/{endpoint}"
    return requests.get(url, headers=HEADERS, params=params, timeout=15).json()

def wp_post(endpoint, payload):
    url = f"{SITE}/wp-json/wp/v2/{endpoint}"
    r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
    return r.json()

def jet_rel(parent_id, child_id):
    url = f"{SITE}/wp-json/jet-rel/{REL_ID}"
    body = {"parent_id": parent_id, "child_id": child_id}
    return requests.post(url, headers=HEADERS, json=body, timeout=15).json()

# ───────── STREAMLIT UI ────────────
st.set_page_config(page_title="Relaciones CPT", layout="wide")
st.title("🛠️ Relaciones CPT (JetEngine)")

menu = st.sidebar.radio("Acción", (
    "Ver reseñas de alojamiento",
    "Añadir reseña + vincular",
    "Vincular reseña existente",
))

# -------- Ver reseñas ----------
if menu == "Ver reseñas de alojamiento":
    hoteles = wp_get(CPT_HOTEL, {"per_page": 100})
    hotel_map = {h["title"]["rendered"]: h["id"] for h in hoteles}
    sel = st.selectbox("Selecciona alojamiento", list(hotel_map.keys()))
    if sel:
        hid = hotel_map[sel]
        st.subheader(f"Reseñas de «{sel}»")
        rels = wp_get(f"{CPT_REVIEW}", {"jet_related_to": hid, "per_page":100})
        for r in rels:
            st.write(f"- {r['title']['rendered']} (ID {r['id']})")

# -------- Añadir reseña ----------
elif menu == "Añadir reseña + vincular":
    hoteles = wp_get(CPT_HOTEL, {"per_page": 100})
    hotel_map = {h["title"]["rendered"]: h["id"] for h in hoteles}
    sel = st.selectbox("Alojamiento destino", list(hotel_map.keys()))
    title = st.text_input("Título reseña")
    content = st.text_area("Contenido")
    if st.button("Crear y vincular") and sel and title:
        new = wp_post(CPT_REVIEW, {"title": title, "content": content, "status": "publish"})
        if "id" in new:
            res = jet_rel(hotel_map[sel], new["id"])
            st.success(f"Reseña creada (ID {new['id']}) y vinculada.")
        else:
            st.error(f"Error WP: {new}")

# -------- Vincular ya existente ----------
else:
    hoteles = wp_get(CPT_HOTEL, {"per_page": 100})
    reviews = wp_get(CPT_REVIEW, {"per_page": 100})

    hotel_map  = {h["title"]["rendered"]: h["id"] for h in hoteles}
    review_map = {r["title"]["rendered"]: r["id"] for r in reviews}

    sel_hotel  = st.selectbox("Alojamiento",  list(hotel_map.keys()))
    sel_review = st.selectbox("Reseña", list(review_map.keys()))

    if st.button("Vincular"):
        out = jet_rel(hotel_map[sel_hotel], review_map[sel_review])
        st.success("Vinculación creada" if "success" in json.dumps(out) else str(out))
