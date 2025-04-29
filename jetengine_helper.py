"""
JetEngine Relations Helper – Streamlit (v1)
==========================================

Web‑app interactiva construida con **Streamlit** para gestionar relaciones
JetEngine entre _Alojamientos_ (parent) y _Opiniones_ (child):

1. **Ver reseñas de uno o varios alojamientos**
2. **Añadir reseñas nuevas a un alojamiento** (`context = child`)
3. **Vincular reseña suelta → alojamiento** (`context = parent`)

Requisitos
----------
```bash
pip install streamlit
```

Ejecuta localmente:
```bash
streamlit run jetengine_helper.py
```

También puedes desplegarlo gratis en **Streamlit Cloud** o **Hugging Face Spaces**
(ambas compañías son plataformas SaaS independientes; ninguna pertenece a la otra
ni a OpenAI).

- **Streamlit Cloud** → Propiedad de **Snowflake Inc.** (Snowflake compró Streamlit
  en 2022).
- **Hugging Face Spaces** → Servicio de la empresa **Hugging Face Inc.**

Ambas ofrecen tiers gratuitos para apps ligeras.
"""

import base64
import json
import re
from typing import List
from urllib import request, error

import streamlit as st

# ---------------- Configuración ---------------- #
API_BASE = "https://triptoislands.com/wp-json/jet-rel/12"
SEP_REGEX = re.compile(r"[\s,\.]+")

# — Autenticación opcional (Application‑Password) —
USER = st.secrets.get("wp_user", "")
APP_PASS = st.secrets.get("wp_app_pass", "")
HEADERS = {"Content-Type": "application/json"}
if USER and APP_PASS:
    token = base64.b64encode(f"{USER}:{APP_PASS}".encode()).decode()
    HEADERS["Authorization"] = f"Basic {token}"

# ---------------- Utilidades HTTP ---------------- #

def _jet_get(endpoint: str):
    try:
        with request.urlopen(endpoint, timeout=10) as resp:
            if resp.status != 200:
                st.error(f"GET {endpoint} → HTTP {resp.status}")
                return None
            return json.loads(resp.read().decode())
    except Exception as exc:
        st.error(f"GET {endpoint} → {exc}")
        return None


def _jet_post(payload: dict) -> bool:
    data = json.dumps(payload).encode()
    req = request.Request(API_BASE, data=data, headers=HEADERS, method="POST")
    try:
        with request.urlopen(req, timeout=10) as resp:
            if 200 <= resp.status < 300:
                return True
            st.error(f"POST → HTTP {resp.status}")
            return False
    except Exception as exc:
        st.error(f"POST → {exc}")
        return False


def serializar(ids: List[str]) -> str:
    elementos = ''.join(f'i:{i};s:{len(v)}:"{v}";' for i, v in enumerate(ids))
    return f'a:{len(ids)}:{{{elementos}}}'

# ---------------- UI ---------------- #
st.set_page_config(page_title="JetEngine Relations Helper", layout="wide")
st.title("🛠️ JetEngine Relations Helper – Streamlit")

opcion = st.sidebar.radio("Selecciona acción", (
    "Ver reseñas de alojamiento",
    "Añadir reseñas a alojamiento",
    "Vincular reseña → alojamiento",
))

# --- 1) Ver reseñas --- #
if opcion == "Ver reseñas de alojamiento":
    entrada = st.text_input("IDs de alojamientos (coma / espacio / punto)")
    if st.button("Consultar") and entrada:
        parent_ids = [x for x in SEP_REGEX.split(entrada) if x.isdigit()]
        for pid in parent_ids:
            st.subheader(f"Alojamiento ID {pid}")
            data = _jet_get(f"{API_BASE}/children/{pid}")
            if not data:
                continue
            st.json(data)
            childs = [str(d.get("child_object_id")) for d in data if "child_object_id" in d]
            if childs:
                st.write("**Child IDs:**", ", ".join(childs))
                st.code(serializar(childs), language="text")
            else:
                st.info("Sin child IDs válidos")

# --- 2) Añadir reseñas --- #
elif opcion == "Añadir reseñas a alojamiento":
    parent_id = st.text_input("ID de alojamiento")
    nuevos = st.text_input("IDs de las nuevas reseñas (coma / espacio / punto)")
    if st.button("Añadir") and parent_id.isdigit() and nuevos:
        child_ids = [x for x in SEP_REGEX.split(nuevos) if x.isdigit()]
        ok = True
        for cid in child_ids:
            ok &= _jet_post({
                "parent_id": int(parent_id),
                "child_id": int(cid),
                "context": "child",
                "store_items_type": "update",
            })
        if ok:
            st.success("Añadidas correctamente. Resultado:")
            st.experimental_rerun()

# --- 3) Vincular reseña suelta --- #
else:
    child_id = st.text_input("ID de la reseña")
    parent_id = st.text_input("ID del alojamiento a vincular")
    if st.button("Vincular") and child_id.isdigit() and parent_id.isdigit():
        if _jet_post({
            "parent_id": int(parent_id),
            "child_id": int(child_id),
            "context": "parent",
            "store_items_type": "update",
        }):
            st.success("Reseña vinculada correctamente. Resultado:")
            st.experimental_rerun()
