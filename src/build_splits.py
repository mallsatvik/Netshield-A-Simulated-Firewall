import os, numpy as np
from sklearn.model_selection import train_test_split

npz = "data/processed/payload_images.npz"
outdir = "data/splits"
os.makedirs(outdir, exist_ok=True)

data = np.load(npz)
X, y = data["X"], data["y"]

X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=42)

np.savez_compressed(os.path.join(outdir, "train.npz"), X=X_train, y=y_train)
np.savez_compressed(os.path.join(outdir, "val.npz"), X=X_val, y=y_val)
np.savez_compressed(os.path.join(outdir, "test.npz"), X=X_test, y=y_test)

print("Saved splits to", outdir)
