# =========================
# 📦 IMPORTS
# =========================
import os
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np

# =========================
# 🎨 UI
# =========================
st.set_page_config(
    page_title="Aves 🐦",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Identificador de Especies de Aves (modo rápido)")

st.markdown("Sube una imagen y obtén una predicción rápida del modelo.")

st.divider()

# =========================
# 🧠 MODELO ULTRA RÁPIDO
# =========================
MODEL_PATH = "modelo_ultra_rapido.keras"

@st.cache_resource
def load_model_cached():
    if not os.path.exists(MODEL_PATH):
        st.error("❌ No se encuentra el modelo rápido (.keras)")
        st.stop()

    return tf.keras.models.load_model(MODEL_PATH)

model = load_model_cached()

# =========================
# 📂 CLASES (puedes mantener las 200)
# =========================
class_names = [
    "Black_Footed_Albatross","Laysan_Albatross","Sooty_Albatross",
    "Groove_billed_Ani","Crested_Auklet","Least_Auklet","Parakeet_Auklet","Rhinoceros_Auklet",
    "Brewer_Blackbird","Red_winged_Blackbird","Rusty_Blackbird","Yellow_headed_Blackbird",
    "Bobolink","Indigo_Bunting","Lazuli_Bunting","Painted_Bunting",
    "Cardinal","Spotted_Catbird","Gray_Catbird","Yellow_breasted_Chat",
    "Eastern_Towhee","Chuck_will_Widow","Brandt_Cormorant","Red_faced_Cormorant",
    "Pelagic_Cormorant","Bronzed_Cowbird","Shiny_Cowbird","Brown_Creeper",
    "American_Crow","Fish_Crow","Black_billed_Cuckoo","Mangrove_Cuckoo",
    "Yellow_billed_Cuckoo","Gray_crowned_Rosy_Finch","Purple_Finch","Northern_Flicker",
    "Acadian_Flycatcher","Great_Crested_Flycatcher","Least_Flycatcher","Olive_sided_Flycatcher",
    "Scissor_tailed_Flycatcher","Vermilion_Flycatcher","Yellow_bellied_Flycatcher","Frigatebird",
    "Northern_Fulmar","Gadwall","American_Goldfinch","European_Goldfinch",
    "Boat_tailed_Grackle","Eared_Grebe","Horned_Grebe","Pied_billed_Grebe",
    "Western_Grebe","Blue_Grosbeak","Evening_Grosbeak","Pine_Grosbeak",
    "Rose_breasted_Grosbeak","Pigeon_Guillemot","California_Gull","Glaucous_winged_Gull",
    "Heermann_Gull","Herring_Gull","Ivory_Gull","Ring_billed_Gull",
    "Slaty_backed_Gull","Western_Gull","Anna_Hummingbird","Ruby_throated_Hummingbird",
    "Rufous_Hummingbird","Green_Violetear","Long_tailed_Jaeger","Pomarine_Jaeger",
    "Blue_Jay","Florida_Jay","Green_Jay","Dark_eyed_Junco",
    "Tropical_Kingbird","Gray_Kingbird","Belted_Kingfisher","Green_Kingfisher",
    "Pied_Kingfisher","Ringed_Kingfisher","White_breasted_Kingfisher","Red_legged_Kittiwake",
    "Horned_Lark","Pacific_Loon","Mallard","Western_Meadowlark",
    "Hooded_Merganser","Red_breasted_Merganser","Mockingbird","Nighthawk",
    "Clark_Nutcracker","White_breasted_Nuthatch","Baltimore_Oriole","Hooded_Oriole",
    "Orchard_Oriole","Scott_Oriole","Ovenbird","Brown_Pelican",
    "White_Pelican","Western_Wood_Pewee","Sayornis","American_Pipit",
    "Whip_poor_Will","Horned_Puffin","Common_Raven","White_necked_Raven",
    "American_Redstart","Geococcyx","Loggerhead_Shrike","Great_Grey_Shrike",
    "Common_Yellowthroat"
]

# =========================
# 📤 UPLOAD
# =========================
uploaded_file = st.file_uploader("📤 Sube una imagen", type=["jpg","jpeg","png"])

# =========================
# 🔍 PREDICCIÓN
# =========================
if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, use_container_width=True)

    img = image.resize((128, 128))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array)

    idx = np.argmax(pred)
    clase = class_names[idx]
    confianza = float(np.max(pred))

    st.divider()

    st.subheader(f"🧠 Resultado: {clase}")

    if confianza < 0.80:
        st.warning(f"⚠ Confianza baja: {confianza:.2%}")
    else:
        st.success(f"✅ Confianza alta: {confianza:.2%}")

    st.bar_chart(pred[0])
    st.progress(confianza)