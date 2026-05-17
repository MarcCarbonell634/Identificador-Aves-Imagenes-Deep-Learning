import os
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks, optimizers, losses
import datetime

# 🔹 1. CONFIGURACIÓN DE GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"✅ GPU activa: {gpus[0].name}")
else:
    print("️ No se detectó GPU. Se usará CPU (será más lento).")

# 🔹 2. PARÁMETROS
IMG_SIZE = 256          # Resolución alta para distinguir especies similares
BATCH_SIZE = 16         # Si da error de memoria (OOM), cambia a 8
NUM_CLASES = 200        # CUB-200-2011 tiene exactamente 200 clases
EPOCHS = 100
data_dir = './images'   # Carpeta con las subcarpetas de cada clase

print(f"📂 Dataset: {os.path.abspath(data_dir)}")
print(f"📐 Resolución: {IMG_SIZE}x{IMG_SIZE} | Clases: {NUM_CLASES}\n")

# 🔹 3. CARGA DE DATOS
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, validation_split=0.2, subset="training", seed=42,
    image_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE, label_mode='categorical'
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, validation_split=0.2, subset="validation", seed=42,
    image_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE, label_mode='categorical'
)

# ✅ CORRECCIÓN: Extraer class_names ANTES de cache/prefetch
class_names = train_ds.class_names
print(f"✅ Clases cargadas: {len(class_names)}")

# 🔹 4. DATA AUGMENTATION (Fine-Grained)
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.12),
    layers.RandomZoom(0.15),
    layers.RandomTranslation(0.1, 0.1),
    layers.RandomContrast(0.2),
])

# Optimización de pipeline
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# 🔹 5. MODELO: TRANSFER LEARNING (EfficientNetB4)
print("\n📦 Cargando EfficientNetB4 pre-entrenado...")
base_model = tf.keras.applications.EfficientNetB4(
    include_top=False, weights='imagenet', input_shape=(IMG_SIZE, IMG_SIZE, 3), pooling='avg'
)
base_model.trainable = False  # Congelado inicialmente

inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = data_augmentation(inputs)
x = tf.keras.applications.efficientnet.preprocess_input(x)
x = base_model(x, training=False)
x = layers.Dropout(0.4)(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(NUM_CLASES, activation='softmax', dtype='float32')(x)

model = models.Model(inputs, outputs)

# 🔹 6. FASE 1: ENTRENAR SOLO EL CABEZAL
print("\n FASE 1: Entrenando capas superiores (base congelada)")
model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-3),
    loss=losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
)

# Callbacks
log_dir = f"./logs/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
tb = callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1, write_images=True)
es1 = callbacks.EarlyStopping('val_accuracy', patience=10, restore_best_weights=True, verbose=1)
rlr1 = callbacks.ReduceLROnPlateau('val_loss', factor=0.5, patience=5, min_lr=1e-6, verbose=1)

# ✅ CHECKPOINT: Guarda automáticamente el mejor modelo
ckpt = callbacks.ModelCheckpoint(
    'mejor_modelo.keras', 
    monitor='val_accuracy', 
    save_best_only=True, 
    mode='max', 
    verbose=1
)

history1 = model.fit(
    train_ds, validation_data=val_ds, epochs=30,
    callbacks=[tb, es1, rlr1, ckpt], verbose=1
)

# 🔹 7. FASE 2: FINE-TUNING (Descongelar últimas capas)
print("\n🔧 FASE 2: Fine-tuning (descongelando últimas 40 capas)")
base_model.trainable = True
for layer in base_model.layers[:-40]:
    layer.trainable = False

# Learning rate más bajo para ajustes finos
model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-4),
    loss=losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
)

es2 = callbacks.EarlyStopping('val_accuracy', patience=15, restore_best_weights=True, verbose=1)
rlr2 = callbacks.ReduceLROnPlateau('val_loss', factor=0.5, patience=7, min_lr=1e-7, verbose=1)

history2 = model.fit(
    train_ds, validation_data=val_ds, epochs=70,
    initial_epoch=len(history1.history['loss']),
    callbacks=[tb, es2, rlr2, ckpt], verbose=1
)

#  8. EVALUACIÓN Y GUARDADO FINAL
print("\n💾 Guardando modelo final...")
model.save('modelo_final_cub200.keras')

val_loss, val_acc = model.evaluate(val_ds, verbose=0)
print(f"\n{'='*60}")
print(f"📊 RESULTADOS FINALES")
print(f"{'='*60}")
print(f"✅ Precisión (Top-1): {val_acc*100:.2f}%")
print(f"🎯 Meta 80%: {'✅ ALCANZADA' if val_acc >= 0.80 else '⏳ Muy cerca, el checkpoint ya tiene lo mejor'}")
print(f"{'='*60}\n")

print(f" El mejor modelo se guardó como: mejor_modelo.keras")
print(f"📊 TensorBoard: tensorboard --logdir {log_dir}")
print("   Abre en tu navegador: http://localhost:6006")