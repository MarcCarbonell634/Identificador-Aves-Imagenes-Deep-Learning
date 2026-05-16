# =========================
# 📦 IMPORTS
# =========================
import os
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import gdown

# =========================
# 🎨 CONFIG
# =========================
st.set_page_config(
    page_title="Identificador de Aves",
    page_icon="🐦",
    layout="centered"
)

st.markdown(
    """
    <div style="text-align:center;">
        <h1>🐦 Sistema de Identificador de Especies de Aves</h1>
        <p style="color:gray;">Sube una imagen y el modelo intentará identificar la especie</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================
# ☁️ MODELO
# =========================
MODEL_PATH = "modelo_prueba_1.keras"
FILE_ID = "1mNs4yc3oF-z1LVPIe_OJ1HzHIZtCXh8m"

if not os.path.exists(MODEL_PATH):
    st.info("📥 Descargando modelo...")
    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    gdown.download(url, MODEL_PATH, quiet=False)

@st.cache_resource
def load_model_cached():
    return tf.keras.models.load_model(MODEL_PATH)

model = load_model_cached()

# =========================
# 📂 200 CLASES (COMPLETO)
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
    "Baird_Sparrow","Black_throated_Sparrow","Brewer_Sparrow","Chipping_Sparrow",
    "Clay_colored_Sparrow","House_Sparrow","Field_Sparrow","Fox_Sparrow",
    "Grasshopper_Sparrow","Harris_Sparrow","Henslow_Sparrow","Le_Conte_Sparrow",
    "Lincoln_Sparrow","Nelson_Sharp_tailed_Sparrow","Savannah_Sparrow","Seaside_Sparrow",
    "Song_Sparrow","Tree_Sparrow","Vesper_Sparrow","White_crowned_Sparrow",
    "White_throated_Sparrow","Cape_Glossy_Starling","Bank_Swallow","Barn_Swallow",
    "Cliff_Swallow","Tree_Swallow","Scarlet_Tanager","Summer_Tanager",
    "Artic_Tern","Black_Tern","Caspian_Tern","Common_Tern",
    "Elegant_Tern","Forsters_Tern","Least_Tern","Green_tailed_Towhee",
    "Brown_Thrasher","Sage_Thrasher","Black_capped_Vireo","Blue_headed_Vireo",
    "Philadelphia_Vireo","Red_eyed_Vireo","Warbling_Vireo","White_eyed_Vireo",
    "Yellow_throated_Vireo","Bay_breasted_Warbler","Black_and_white_Warbler","Black_throated_Blue_Warbler",
    "Blue_winged_Warbler","Canada_Warbler","Cape_May_Warbler","Cerulean_Warbler",
    "Chestnut_sided_Warbler","Golden_winged_Warbler","Hooded_Warbler","Kentucky_Warbler",
    "Magnolia_Warbler","Mourning_Warbler","Myrtle_Warbler","Nashville_Warbler",
    "Orange_crowned_Warbler","Palm_Warbler","Pine_Warbler","Prairie_Warbler",
    "Prothonotary_Warbler","Swainson_Warbler","Tennessee_Warbler","Wilson_Warbler",
    "Worm_eating_Warbler","Yellow_Warbler","Northern_Waterthrush","Louisiana_Waterthrush",
    "Bohemian_Waxwing","Cedar_Waxwing","American_Three_toed_Woodpecker","Pileated_Woodpecker",
    "Red_bellied_Woodpecker","Red_cockaded_Woodpecker","Red_headed_Woodpecker","Downy_Woodpecker",
    "Bewick_Wren","Cactus_Wren","Carolina_Wren","House_Wren",
    "Marsh_Wren","Rock_Wren","Winter_Wren","Common_Yellowthroat"
]

# =========================
# 📤 UPLOAD
# =========================
uploaded_file = st.file_uploader("📤 Sube una imagen de un ave", type=["jpg", "jpeg", "png"])

# =========================
# 🔍 PREDICCIÓN
# =========================
if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Imagen subida", use_container_width=True)

    with col2:
        st.info("🔎 Analizando imagen...")

    img = image.resize((128, 128))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array)

    clase_idx = np.argmax(pred)
    clase = class_names[clase_idx]
    confianza = float(np.max(pred))

    st.divider()

    # =========================
    # 📊 RESULTADO + UMBRAL
    # =========================
    st.subheader(f"🧠 Resultado: {clase}")

    if confianza < 0.80:
        st.warning(f"⚠ Confianza baja: {confianza:.2%}")
    else:
        st.success(f"✅ Confianza alta: {confianza:.2%}")

    # =========================
    # 📊 PROBABILIDADES
    # =========================
    st.subheader("📊 Probabilidades del modelo")
    st.bar_chart(pred[0])

    st.progress(confianza)