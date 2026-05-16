# =========================
# 🧠 CARGAR MODELO (FIX STREAMLIT)
# =========================
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import streamlit as st

MODEL_PATH = "modelo_prueba_1.keras"

# Comprobar que existe el archivo
if not os.path.exists(MODEL_PATH):
    st.error("❌ No se encontró el modelo. Revisa que esté en el repositorio.")
    st.stop()

# Cargar modelo (robusto)
model = tf.keras.models.load_model(MODEL_PATH, compile=False)