<div align="center">

# ⚡ CONSTRUCTION ALERT SYSTEM

### *Dual-Layer Perimeter Security — Vision + Seismic Intelligence*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-660066?style=for-the-badge&logo=eclipsemosquitto&logoColor=white)](https://mosquitto.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF4081?style=for-the-badge)](https://ultralytics.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Zero-lag, dual-sensor perimeter protection for construction sites.**
> Combines real-time computer vision with seismic footfall detection to catch every intrusion — even in the dark.

</div>

---

## 🧠 What Is This?

Construction sites are high-value, high-risk zones — expensive equipment, open perimeters, 24/7 vulnerability. **Construction Alert System** is a smart, edge-deployable security platform that fuses two detection modalities:

| Layer | Technology | What it catches |
|-------|-----------|-----------------|
| 👁️ **Vision** | YOLOv8 + OpenCV | Humans entering restricted zones |
| 🌍 **Seismic** | MQTT + Butterworth DSP | Footfall vibrations through ground sensors |

Both channels feed into a **real-time web dashboard** with live video streaming, alert management, and GPIO-driven buzzers — all running on a Raspberry Pi or any Linux box.

---

## 🚀 Features

- 🎯 **Human-only alerts** — detects people, ignores birds and other false positives
- 🗺️ **Custom exclusion zones** — draw polygonal alert zones directly on the video feed
- 📡 **MQTT seismic pipeline** — subscribes to ground sensor data over MQTT in real-time
- 🔬 **Butterworth band-pass filter** — 2–15 Hz DSP filtering to isolate footfall frequencies
- ⏱️ **Temporal smoothing** — requires 5 consecutive frames before firing an alarm (no ghost alerts)
- 📺 **Live Mission Control dashboard** — real-time MJPEG video feed with overlaid detection boxes
- 🔔 **GPIO buzzer integration** — physical alert via Raspberry Pi GPIO pin 18
- 🐳 **Fully containerized** — Docker Compose spins up the app + Mosquitto broker in one command
- 🧪 **Simulator mode** — runs fully offline with synthetic seismic data if no MQTT broker is found
- 📊 **Intrusion counter & event log** — tracks every alert with a timestamp

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  CONSTRUCTION ALERT SYSTEM               │
│                                                         │
│   ┌──────────────┐        ┌───────────────────────┐    │
│   │  SEISMIC     │        │    VISION PIPELINE    │    │
│   │  SENSOR      │        │                       │    │
│   │  (MQTT)      │        │  Camera → YOLOv8 →   │    │
│   │     │        │        │  Zone Check → Alert   │    │
│   │     ▼        │        │                       │    │
│   │ Butterworth  │        └──────────┬────────────┘    │
│   │ Band-Pass    │                   │                  │
│   │ 2–15Hz DSP   │                   │                  │
│   │     │        │                   │                  │
│   └─────┼────────┘                   │                  │
│         │                            │                  │
│         └──────────┬─────────────────┘                  │
│                    ▼                                     │
│            ┌───────────────┐                            │
│            │  ALERT ENGINE │                            │
│            │  GPIO Buzzer  │                            │
│            │  Web Dashboard│                            │
│            └───────────────┘                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
construction-alert-system/
│
├── main.py                  # 🚀 Entry point — boots all subsystems
├── config.py                # ⚙️  Central config (MQTT, GPIO, sampling rate)
├── requirements.txt         # 📦 Python dependencies
├── Dockerfile               # 🐳 Container definition
├── docker-compose.yml       # 🐳 App + Mosquitto broker orchestration
├── setup.sh                 # 🛠️  One-shot environment setup script
│
├── app/
│   ├── core/
│   │   ├── camera.py        # 📷 Video capture & MJPEG streaming
│   │   ├── detector.py      # 🔍 YOLOv8 object detection wrapper
│   │   ├── processor.py     # 🖥️  Frame pipeline (detect → zone check → alert)
│   │   ├── inference.py     # 🤖 Seismic signal inference engine
│   │   ├── signal_processing.py  # 📡 Butterworth band-pass DSP filter
│   │   ├── mqtt_client.py   # 📨 MQTT subscriber for seismic data
│   │   ├── gpio_controller.py    # 🔔 Raspberry Pi GPIO buzzer driver
│   │   └── geometry.py      # 📐 Polygon zone intersection math
│   │
│   └── web/
│       ├── templates/       # 🌐 Jinja2 HTML dashboard
│       └── static/          # 🎨 JS + CSS (Mission Control UI)
│
└── tests/
    ├── test_zones.py        # ✅ Zone geometry tests
    ├── test_detector.py     # ✅ Detection pipeline tests
    └── test_core.py         # ✅ Core module integration tests
```

---

## ⚙️ Quick Start

### Option A — Docker (Recommended) 🐳

```bash
git clone https://github.com/aadhiii2529/JUSFASAKE-.git
cd JUSFASAKE-
docker-compose up --build
```

That's it. The app starts on **http://localhost:5000** and Mosquitto runs on **port 1883**.

---

### Option B — Local Python

**1. Clone & enter the repo**
```bash
git clone https://github.com/aadhiii2529/JUSFASAKE-.git
cd JUSFASAKE-
```

**2. Create a virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
# Optional: for real YOLOv8 (not mock)
pip install ultralytics
```

**4. Run**
```bash
python main.py
```

Open **http://localhost:5000** in your browser.

> 💡 No MQTT broker? No problem. The system auto-starts in **Simulator Mode** with synthetic seismic data.

---

## 🔧 Configuration

All settings live in `config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER` | `localhost` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_TOPIC` | `seismic/data` | Topic for ground sensor data |
| `SECRET_KEY` | `dev-secret-key` | Flask session secret |

**Signal Processing (hardcoded, tunable in config.py):**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `SAMPLING_RATE` | 100 Hz | Sensor sampling frequency |
| `FILTER_LOWCUT` | 2.0 Hz | Low end of footfall frequency band |
| `FILTER_HIGHCUT` | 15.0 Hz | High end of footfall frequency band |
| `BUZZER_PIN` | GPIO 18 | Raspberry Pi alarm output pin |

---

## 📡 MQTT Payload Format

Publish seismic sensor data to the `seismic/data` topic in this format:

```json
{
  "data": [0.12, 0.08, 0.15, 0.09, 0.11, 0.13, 0.07, 0.10, 0.14, 0.08],
  "timestamp": 1709123456.789
}
```

The system will:
1. Apply a **5th-order Butterworth band-pass filter** (2–15 Hz)
2. Run the **inference engine** with the current sensitivity threshold
3. Trigger the alarm if footfall is detected

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_zones.py -v
```

---

## 🛠️ Hardware Setup (Raspberry Pi)

```
Raspberry Pi
├── GPIO Pin 18  ────────► Buzzer (+)
├── GND          ────────► Buzzer (-)
├── USB          ────────► Camera (or CSI ribbon)
└── Network      ────────► MQTT Broker / LAN
```

Install GPIO support:
```bash
pip install RPi.GPIO
```

> ⚠️ GPIO is mocked automatically on non-Pi hardware — safe to develop on any machine.

---

## 🤖 Detection Logic

```
Frame captured
     │
     ▼
YOLOv8 inference (all objects)
     │
     ├─► Bird detected?  → Draw orange box, IGNORE for alerts
     │
     └─► Person detected?
              │
              ▼
         Inside alert zone?
              │
              ├─► NO  → Continue
              │
              └─► YES → Increment persistence counter
                              │
                         5+ consecutive frames?
                              │
                              └─► ALARM 🚨 (vision trigger)
```

---

## 📦 Tech Stack

| Technology | Role |
|-----------|------|
| **Python 3.10+** | Core runtime |
| **Flask 3.0** | Web server & REST API |
| **OpenCV 4.8** | Video capture & frame processing |
| **YOLOv8 (Ultralytics)** | Real-time object detection |
| **SciPy / NumPy** | DSP signal filtering |
| **Paho-MQTT** | MQTT seismic data subscriber |
| **Shapely** | Polygon zone geometry |
| **Waitress** | Production WSGI server |
| **Docker + Mosquitto** | Container orchestration + MQTT broker |
| **RPi.GPIO** | Physical buzzer control (Raspberry Pi) |

---

## 📜 License

MIT License — free to use, modify, and deploy. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for the edge. Runs anywhere. Catches everyone.**

*Star ⭐ the repo if this saved your site.*

</div>
