"""
JetEngine Relations Helper – Streamlit (v1.2)
============================================

Mejoras:
• Tras **Añadir** o **Vincular** reseñas muestra un mensaje claro:
  “Reseñas 886, 887 añadidas al alojamiento 671”.
• Limpia los campos de entrada mediante `st.session_state` para que queden vacíos.

Requisitos
```bash
pip install streamlit>=1.25
```
"""

import base64
import json
import re
from typing import List
from urllib import error, request

import streamlit as st

# ---------------- Configuración ---------------- #
API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
SEP = re.compile(r"[\s,\.]+")
HEADERS = {"Content-Type": "application/json"}

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

# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="JetEngine Helper", layout="wide")
st.title("🛠️ JetEngine Relations Helper – Streamlit")

op = st.sidebar.radio("Selecciona acción", (
    "Ver reseñas de alojamiento",
    "Añadir reseñas a alojamiento",
    "Vincular reseña → alojamiento",
))

# --- Ver reseñas --- #
if op == "Ver reseñas de alojamiento":
    ids_in = st.text_input("IDs de alojamientos (coma / espacio / punto)")
    if st.button("Consultar") and ids_in:
        for pid in [x for x in SEP.split(ids_in) if x.isdigit()]:
            st.subheader(f"Alojamiento {pid}")
            data = _get(f"{API_BASE}/children/{pid}")
            if not data:
                continue
            st.json(data)
            childs = [str(d.get("child_object_id")) for d in data if "child_object_id" in d]
            if childs:
                st.write("**Child IDs:**", ", ".join(childs))
                st.code(serializar(childs))
            else:
                st.info("Sin child IDs")

# --- Añadir reseñas --- #
elif op == "Añadir reseñas a alojamiento":
    parent_id = st.text_input("ID de alojamiento", key="parent_add")
    new_ids = st.text_input("IDs de nuevas reseñas", key="childs_add")
    if st.button("Añadir") and parent_id.isdigit() and new_ids:
        cids = [x for x in SEP.split(new_ids) if x.isdigit()]
        if not cids:
            st.warning("No hay IDs válidos")
        else:
            ok = all(_post({
                "parent_id": int(parent_id),
                "child_id": int(cid),
                "context": "child",
                "store_items_type": "update",
            }) for cid in cids)
            if ok:
                st.success(f"Reseñas {', '.join(cids)} añadidas al alojamiento {parent_id}")
                st.session_state.parent_add = ""
                st.session_state.childs_add = ""
            else:
                st.error("Alguna petición falló")

# --- Vincular reseña --- #
else:
    child_id = st.text_input("ID de reseña", key="child_link")
    parent_id = st.text_input("ID de alojamiento", key="parent_link")
    if st.button("Vincular") and child_id.isdigit() and parent_id.isdigit():
        if _post({
            "parent_id": int(parent_id),
            "child_id": int(child_id),
            "context": "parent",
            "store_items_type": "update",
        }):
            st.success(f"Reseña {child_id} vinculada al alojamiento {parent_id}")
            st.session_state.child_link = ""
            st.session_state.parent_link = ""
        else:
            st.error("Error en la vinculación")
