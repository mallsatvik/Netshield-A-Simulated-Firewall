import os, argparse, numpy as np
from scapy.all import PcapReader, Raw
from tqdm import tqdm
from src.utils import bytes_to_image

def extract_samples(pcap_path, label):
    X, y = [], []
    with PcapReader(pcap_path) as rd:
        for pkt in tqdm(rd, desc=os.path.basename(pcap_path)):
            if Raw in pkt:
                img = bytes_to_image(bytes(pkt[Raw].load))
                X.append(img)
                y.append(label)
    return np.array(X), np.array(y)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--benign", required=True, help="path to benign pcap")
    ap.add_argument("--attack", required=True, help="path to attack pcap")
    ap.add_argument("--out", default="data/processed/payload_images.npz")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    Xb, yb = extract_samples(args.benign, 0)
    Xa, ya = extract_samples(args.attack, 1)

    X = np.concatenate([Xb, Xa], axis=0)
    y = np.concatenate([yb, ya], axis=0)

    idx = np.random.permutation(len(y))
    X, y = X[idx], y[idx]

    np.savez_compressed(args.out, X=X, y=y)
    print("Saved:", args.out)
