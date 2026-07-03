#!/usr/bin/env python3
"""
Live packet capture -> CNN classifier -> n8n webhook

Usage:
  sudo python -m src.live_infer_scapy \
    --interface en0 \
    --webhook-url "https://.../webhook/cnn-firewall" \
    --model models/cnn_firewall.h5 \
    --filter "tcp and (port 80 or port 443)"

If you set IFACE, N8N_WEBHOOK_URL, THRESH, MODEL_PATH in your .env, the script will
use those values as defaults.
"""
import os
import time
import argparse
import requests
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from scapy.all import sniff, IP, TCP, UDP, Raw, get_if_list
from src.utils import bytes_to_image

# load .env values (if present)
load_dotenv()
DEFAULT_IFACE = os.getenv("IFACE", "en0")       # fallback to en0 instead of wlan0 for macs
DEFAULT_WEBHOOK = os.getenv("N8N_WEBHOOK_URL", "")
DEFAULT_THRESH = float(os.getenv("THRESH", "0.9"))
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "models/cnn_firewall.h5")

# CLI args
parser = argparse.ArgumentParser(description="Live PCAP -> CNN classifier -> n8n webhook")
parser.add_argument("--interface", "-i", default=DEFAULT_IFACE, help="Network interface to sniff (e.g. en0)")
parser.add_argument("--webhook-url", "-w", default=DEFAULT_WEBHOOK, help="n8n webhook URL to POST alerts to")
parser.add_argument("--model", "-m", default=DEFAULT_MODEL_PATH, help="Path to saved keras model (.h5)")
parser.add_argument("--filter", "-f", default="ip", help="BPF filter string (tcp, udp, port 80, etc.)")
parser.add_argument("--thresh", "-t", type=float, default=DEFAULT_THRESH, help="Threshold for blocking (0-1)")
args = parser.parse_args()

IFACE = args.interface
N8N_WEBHOOK_URL = args.webhook_url
MODEL_PATH = args.model
THRESH = args.thresh
BPF_FILTER = args.filter

# validate interface exists (helpful message if not)
available_ifaces = get_if_list()
if IFACE not in available_ifaces:
    print("ERROR: requested interface not found:", IFACE)
    print("Available interfaces:", ", ".join(available_ifaces))
    raise SystemExit(1)

# load model safely
try:
    print("Loading model from:", MODEL_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)
    # optionally compile so metrics exist (not required for inference)
    try:
        model.compile()
    except Exception:
        # ignore compile errors — not necessary for predict
        pass
    print("Model loaded successfully.")
except Exception as e:
    print("Failed to load model:", MODEL_PATH)
    raise

def classify(payload: bytes) -> float:
    """Convert payload bytes to model input and return probability/score."""
    img = bytes_to_image(payload)
    x = np.expand_dims(img, 0)
    prob = float(model.predict(x, verbose=0)[0][0])
    return prob

def alert_n8n(event: dict):
    """POST event to n8n webhook; swallow errors gracefully."""
    if not N8N_WEBHOOK_URL:
        return
    try:
        requests.post(N8N_WEBHOOK_URL, json=event, timeout=10)
    except Exception as exc:
        # Log the exception so you know webhook failed (but don't crash)
        print("Warning: failed to post to n8n webhook:", exc)

def handler(pkt):
    """Scapy packet handler — classify payload and optionally alert."""
    if Raw not in pkt:
        return

    try:
        payload = bytes(pkt[Raw].load)
    except Exception:
        return

    try:
        score = classify(payload)
    except Exception as exc:
        print("Error during classification:", exc)
        return

    verdict = "BLOCK" if score >= THRESH else "ALLOW"

    src = pkt[IP].src if IP in pkt else "NA"
    dst = pkt[IP].dst if IP in pkt else "NA"
    # sport/dport handling for both TCP/UDP
    if TCP in pkt:
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
    elif UDP in pkt:
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport
    else:
        sport, dport = -1, -1

    ts = time.time()
    print(f"[{verdict}] {src}:{sport} -> {dst}:{dport} | score={score:.3f} ts={ts:.0f}")

    if verdict == "BLOCK":
        event = {
            "timestamp": ts,
            "src": src,
            "dst": dst,
            "sport": sport,
            "dport": dport,
            "score": score,
            "action": verdict,
        }
        alert_n8n(event)

def main():
    print(f"Starting live sniff on interface '{IFACE}' with filter '{BPF_FILTER}'")
    print("Press Ctrl+C to stop.")
    try:
        sniff(iface=IFACE, prn=handler, store=False, filter=BPF_FILTER)
    except KeyboardInterrupt:
        print("\nStopped by user (KeyboardInterrupt).")
    except Exception as e:
        print("Sniffer error:", e)

if __name__ == "__main__":
    main()
