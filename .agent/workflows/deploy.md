---
description: How to deploy the Construction Alert System
---

## Deployment Options

You can deploy the Construction Alert System using standard Python or Docker.

### Option 1: Standard Python Deployment (Recommended for Development/Windows)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you are on a Raspberry Pi, ensure you have `RPi.GPIO` installed.*

2. **Run the Application**:
   ```bash
   python main.py
   ```
   The dashboard will be available at `http://localhost:5000`.

### Option 2: Docker Deployment (Recommended for Production/Linux)

1. **Build and Start**:
   ```bash
   docker-compose up --build -d
   ```
   This will start the application and a local MQTT broker (Mosquitto) for seismic data.

2. **Check Logs**:
   ```bash
   docker-compose logs -f app
   ```

---

## Hardware Setup (Raspberry Pi)

1. **GPIO Wiring**:
   - Connect your High-DB Buzzer to **GPIO 18** (Physical pin 12) and GND.
2. **Camera**:
   - Enable the camera interface via `raspi-config`.
   - The system automatically detects `/dev/video0`.
3. **Seismic Sensors**:
   - Configure your seismic nodes to publish JSON data to the MQTT topic `seismic/data` in the format: `{"data": [0.1, 0.2, ...]}`.

## Production Tuning

- **Sensitivity**: Use the web dashboard to calibrate the threshold for current ground conditions.
- **Port**: Change the port in `app/web/app.py` or `docker-compose.yml` if needed.
- **Static Files**: For heavy production use, consider serving `/static` via Nginx.
