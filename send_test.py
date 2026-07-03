import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK = os.getenv("N8N_WEBHOOK_URL")

event = {
    "timestamp": time.time(),
    "src": "8.8.8.8",
    "dst": "10.0.0.5",
    "sport": 443,
    "dport": 80,
    "score": 0.95,
    "action": "ALLOW"
}

print("Sending test alert to n8n...")
r = requests.post(WEBHOOK, json=event, timeout=5)
print("Status code:", r.status_code)
print("Response:", r.text)
