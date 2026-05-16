# =========================
# 📦 IMPORTS
# =========================
import os
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import gdown

# =========================
# ⚙️ CONFIG
# =========================
MODEL_PATH = "modelo_prueba_ultra_rapido.keras"  # o el grande si usas Drive
FILE_ID = "1mNs4yc3oF-z1LVPIe_OJ1HzHIZtCXh8m"

# =========================
# 🧠 CARGA DEL MODELO
# =========================
@st.cache_resource
def load_model():

    if not os.path.exists(MODEL_PATH):
        st.info("📥 Descargando modelo desde Drive...")

        url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)

    return tf.keras.models.load_model(MODEL_PATH)

model = load_model()

# =========================
# 📂 CLASES (LIMPIEZA EN MEMORIA)
# =========================
with open("classes.txt", "r", encoding="utf-8") as f:
    class_names = []

    for line in f:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        raw = parts[-1]  # "001.Black_footed_Albatross"

        if "." in raw:
            raw = raw.split(".", 1)[1]

        class_names.append(raw)

# =========================
# 🎨 UI
# =========================
st.set_page_config(page_title="🐦 Aves IA", layout="centered")

st.title("🐦 Identificador de Especies de Aves")
st.write("Sube una imagen y el modelo intentará identificarla")

uploaded_file = st.file_uploader("📤 Imagen", type=["jpg", "jpeg", "png"])

# =========================
# 🔍 PREDICCIÓN
# =========================
if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, use_container_width=True)

    # Preprocesado
    img = image.resize((128, 128))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    # Predicción
    pred = model.predict(img)

    idx = np.argmax(pred)
    clase = class_names[idx]
    confianza = float(np.max(pred))

    # =========================
    # 📊 RESULTADOS
    # =========================
    st.subheader(f"🧠 Resultado: {clase}")

    if confianza < 0.80:
        st.warning(f"⚠ Baja confianza: {confianza:.2%}")
    else:
        st.success(f"✅ Alta confianza: {confianza:.2%}")

    st.progress(confianza)

    st.write("📊 Probabilidades por clase:")
    st.bar_chart(pred[0])