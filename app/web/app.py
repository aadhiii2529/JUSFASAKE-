from flask import Flask, render_template, jsonify, request, Response as FlaskResponse
import threading
import time
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global state (in a real app, use a proper store or database)
system_status = {
    "connected": False,
    "last_event": None,
    "sensitivity": 50,  # Threshold for detection
    "zones": [], # List of zone coordinates or IDs
    "alarm_active": False,
    "intrusion_count": 0,
    "location": {
        "name": "Construction Site Alpha",
        "latitude": 0.0,
        "longitude": 0.0
    },
    "camera_url": "0" # Default local camera
}

# Reference to core components (to be injected or imported)
mqtt_client = None
gpio_controller = None
frame_processor = None
camera = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(system_status)

@app.route('/api/sensitivity', methods=['POST'])
def update_sensitivity():
    data = request.json
    system_status['sensitivity'] = float(data.get('value', 50))
    return jsonify({"status": "updated", "sensitivity": system_status['sensitivity']})

@app.route('/api/zones', methods=['GET', 'POST'])
def manage_zones():
    if request.method == 'POST':
        zone = request.json
        system_status['zones'].append(zone)
        return jsonify({"status": "added", "zones": system_status['zones']})
    return jsonify(system_status['zones'])

@app.route('/api/location', methods=['GET', 'POST'])
def manage_location():
    if request.method == 'POST':
        data = request.json
        if 'name' in data:
            system_status['location']['name'] = data['name']
        if 'latitude' in data:
            system_status['location']['latitude'] = float(data['latitude'])
        if 'longitude' in data:
            system_status['location']['longitude'] = float(data['longitude'])
        return jsonify({"status": "updated", "location": system_status['location']})
    return jsonify(system_status['location'])

@app.route('/api/camera', methods=['POST'])
def update_camera():
    data = request.json
    new_url = data.get('url', '')
    
    if str(new_url).strip().upper() == 'LOCAL':
        new_url = '0'
        
    log.info(f"RTSP/Camera Update Request: {new_url}")
    
    if new_url:
        system_status['camera_url'] = new_url
        
        # Access the camera object injected in main.py
        target_camera = getattr(app, 'camera', None)
        
        if target_camera:
            threading.Thread(target=target_camera.update_source, args=(new_url,)).start()
            return jsonify({"status": "updated", "camera_url": new_url})
        else:
            log.warning("Camera not initialized on app instance")
            return jsonify({"status": "updated", "camera_url": new_url, "note": "Camera init pending"}), 200
            
    return jsonify({"status": "error", "message": "No URL provided"}), 400

@app.route('/api/trigger_test', methods=['POST'])
def trigger_test():
    """Manually trigger the buzzer for testing."""
    if gpio_controller:
        gpio_controller.activate_buzzer()
        time.sleep(1)
        gpio_controller.deactivate_buzzer()
        return jsonify({"status": "triggered"})
    return jsonify({"status": "error", "message": "GPIO not initialized"}), 500

@app.route('/api/silence', methods=['POST'])
def silence_alarm():
    system_status['alarm_active'] = False
    if gpio_controller:
        gpio_controller.deactivate_buzzer()
    return jsonify({"status": "silenced"})

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            if frame_processor:
                frame = frame_processor.get_latest_frame()
                if frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                else:
                    # Wait slightly for first frame if processor just started
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
            
            time.sleep(0.033) # ~30fps target
            
    return FlaskResponse(gen(),
                         mimetype='multipart/x-mixed-replace; boundary=frame')

def start_server(port=5000):
    from waitress import serve
    app.logger.info(f"Serving on port {port} with Waitress (threads=50)...")
    serve(app, host='0.0.0.0', port=port, threads=50)
