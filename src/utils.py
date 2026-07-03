import numpy as np
from src.config import IMG_H, IMG_W, MAX_BYTES

def bytes_to_image(payload: bytes) -> np.ndarray:
    """
    Convert a bytes payload to a normalized 32x32x1 numpy image.
    """
    b = np.frombuffer(payload[:MAX_BYTES], dtype=np.uint8)
    if b.size < MAX_BYTES:
        b = np.pad(b, (0, MAX_BYTES - b.size))
    img = b.reshape(IMG_H, IMG_W).astype(np.float32) / 255.0
    return img[..., None]
