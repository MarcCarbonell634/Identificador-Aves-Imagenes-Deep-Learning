import os
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model

st.title("Sistema de Identificador de Especies de Aves")

# 🔍 DEBUG (temporal)
st.write("Archivos en runtime:", os.listdir())

# 🧠 cargar modelo
@st.cache_resource
def load_my_model():
    return tf.keras.models.load_model("modelo_prueba_1.keras", compile=False)

model = load_my_model()