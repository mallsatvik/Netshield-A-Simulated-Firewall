import os, numpy as np, tensorflow as tf
from sklearn.metrics import f1_score
from src.config import IMG_H, IMG_W, CHANNELS, BATCH_SIZE, EPOCHS, MODEL_PATH

def build_model():
    m = tf.keras.Sequential([
        tf.keras.layers.Input((IMG_H, IMG_W, CHANNELS)),
        tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D(2),
        tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D(2),
        tf.keras.layers.Conv2D(128, 3, activation='relu', padding='same'),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    m.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss='binary_crossentropy',
              metrics=[tf.keras.metrics.BinaryAccuracy(name="acc"),
                       tf.keras.metrics.AUC(name="auc"),
                       tf.keras.metrics.Precision(name="prec"),
                       tf.keras.metrics.Recall(name="rec")])
    return m

def load_split(path):
    d = np.load(path)
    return d["X"], d["y"]

if __name__ == "__main__":
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    Xtr, ytr = load_split("data/splits/train.npz")
    Xva, yva = load_split("data/splits/val.npz")

    model = build_model()
    cbs = [
        tf.keras.callbacks.ModelCheckpoint("models/checkpoints/ckpt.keras", monitor="val_auc", mode="max", save_best_only=True),
        tf.keras.callbacks.EarlyStopping(monitor="val_auc", mode="max", patience=4, restore_best_weights=True)
    ]
    os.makedirs("models/checkpoints", exist_ok=True)

    model.fit(Xtr, ytr, validation_data=(Xva, yva),
              epochs=EPOCHS, batch_size=BATCH_SIZE, callbacks=cbs, verbose=2)

    model.save(MODEL_PATH)
    print("Saved model to", MODEL_PATH)

    yprob = model.predict(Xva).ravel()
    yhat = (yprob >= 0.5).astype(int)
    print("Val F1:", f1_score(yva, yhat))
