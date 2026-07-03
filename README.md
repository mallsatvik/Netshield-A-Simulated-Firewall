# 🛡️ NetShield – AI-Powered Simulated Firewall

A real-time network traffic monitoring system that uses a **Convolutional Neural Network (CNN)** to classify packet payloads as benign or suspicious, while integrating with **n8n** to automate email alerts and Google Sheets logging.

---

## 📖 Overview

NetShield is a proof-of-concept AI firewall that combines:

- Deep Learning (TensorFlow/Keras)
- Live Packet Capture (Scapy)
- Network Traffic Analysis
- Workflow Automation (n8n)
- Google Sheets Logging
- Email Notifications

Instead of relying solely on rule-based filtering, NetShield analyzes packet payloads using a CNN and automatically alerts the user when suspicious traffic is detected.

---

## 🚀 Features

- 📡 Live packet sniffing using Scapy
- 🧠 CNN-based packet classification
- ⚡ Real-time inference
- 📊 Google Sheets logging
- 📧 Automatic email alerts
- 🔗 n8n workflow integration
- ⚙️ Adjustable detection threshold
- 🖥️ Live terminal monitoring

---

## 🏗️ System Architecture

```
                 Live Network Traffic
                         │
                         ▼
                  Scapy Packet Capture
                         │
                         ▼
             Payload → 32×32 Image Conversion
                         │
                         ▼
               TensorFlow CNN Classifier
                         │
              ┌──────────┴──────────┐
              │                     │
           ALLOW                 BLOCK
              │                     │
              │             Send JSON to n8n
              │                     │
              │          ┌──────────┴──────────┐
              │          │                     │
              ▼          ▼                     ▼
        Terminal Log  Google Sheets      Email Alert
```

---

# 📂 Project Structure

```
simulated-firewall/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── splits/
│
├── models/
│   └── cnn_firewall.h5
│
├── scripts/
│
├── src/
│   ├── config.py
│   ├── utils.py
│   ├── preprocess_payloadtoimage.py
│   ├── build_splits.py
│   ├── train_cnn_2D.py
│   └── live_infer_scapy.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# 🧠 How It Works

### Step 1 – Capture Traffic

Scapy continuously captures packets from the selected network interface.

---

### Step 2 – Extract Payload

Only packets containing raw payload data are processed.

---

### Step 3 – Convert Payload to Image

The payload bytes are

- truncated/padded
- reshaped into a **32×32 grayscale image**
- normalized between 0 and 1

---

### Step 4 – CNN Classification

The TensorFlow model predicts a probability score.

```
Score ≥ Threshold  → BLOCK
Score < Threshold  → ALLOW
```

---

### Step 5 – Automation

Whenever a packet is classified as **BLOCK**:

- JSON data is sent to n8n
- Google Sheets receives a new row
- An email notification is automatically sent

---

# 📊 Logged Information

Each blocked packet stores

| Field | Description |
|---------|------------|
| Timestamp | Detection time |
| Source IP | Packet source |
| Destination IP | Packet destination |
| Source Port | Sender port |
| Destination Port | Receiver port |
| Score | CNN confidence |
| Action | BLOCK |

---

# 📧 Email Alert

Example email contents:

```
🚨 CNN Firewall Alert

Source IP: 192.168.1.20
Destination IP: 142.251.221.174

Source Port: 51543
Destination Port: 443

Confidence Score: 0.95

Action Taken:
BLOCK

Timestamp:
2025-11-14 18:24:55
```

---

# 📈 Technologies Used

- Python
- TensorFlow / Keras
- NumPy
- Scapy
- Requests
- python-dotenv
- n8n
- Google Sheets API
- Gmail SMTP

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/NetShield-A-Simulated-Firewall.git
```

Move into the folder

```bash
cd NetShield-A-Simulated-Firewall
```

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Configure

Create a `.env` file

```env
N8N_WEBHOOK_URL=https://your-n8n-webhook-url
IFACE=Wi-Fi
THRESH=0.6
```

---

# Run

```bash
sudo python -m src.live_infer_scapy
```

(On Windows, simply run the command without `sudo`.)

---

# Example Output

```
[ALLOW]
192.168.1.15:53211
→
142.251.221.174:443

score = 0.41

-----------------------------------

[BLOCK]
192.168.1.15:53212
→
142.251.221.174:443

score = 0.93

Alert sent to n8n
```

---

# Future Improvements

- Flow-based classification instead of packet-based
- Support for multiple ML models
- Dynamic firewall rule generation
- Dashboard for live analytics
- Explainable AI (Grad-CAM)
- Threat intelligence integration
- Multi-class intrusion detection
- Real-time visualization

---

# Limitations

- Simulated firewall (does not actually block traffic)
- Performance depends on CNN accuracy
- Requires administrator privileges for packet capture
- Trained on a limited dataset

---

# Author

**Satvik Mall**

B.Tech Computer Science Engineering

VIT Chennai

---

## ⭐ If you found this project interesting, consider giving it a star!
