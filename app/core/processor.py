import threading
import time
import cv2
import numpy as np
import logging
from app.core.geometry import is_box_in_zone

logger = logging.getLogger(__name__)

class FrameProcessor:
    def __init__(self, camera, detector, system_status, gpio_controller=None):
        self.camera = camera
        self.detector = detector
        self.system_status = system_status
        self.gpio_controller = gpio_controller
        
        self.latest_frame = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Temporal smoothing
        self.detection_persistence = 0
        self.persistence_threshold = 5 # Number of frames required for stable alert

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Frame Processor background thread started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        while self.running:
            try:
                # 1. Capture
                frame_bytes = self.camera.get_frame()
                
                # 2. Decode
                nparr = np.frombuffer(frame_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    time.sleep(0.01)
                    continue
                
                # 3. Detect
                detections = self.detector.detect(img)
                
                # 4. Process Detections
                something_in_zone = False
                zones = self.system_status.get('zones', [])
                
                for det in detections:
                    bbox = det['bbox']
                    label = det['class']
                    conf = det['conf']
                    
                    x1, y1, x2, y2 = map(int, bbox)
                    color = (0, 255, 0) if label == 'person' else (255, 165, 0) # Green for person, Orange for bird
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    if label == 'person':
                        for zone in zones:
                            if is_box_in_zone(bbox, zone):
                                something_in_zone = True
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                                cv2.putText(img, "HUMAN IN ZONE!", (x1, y2 + 20), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                                break
                    elif label == 'bird':
                        # Draw bird but don't set something_in_zone
                        cv2.putText(img, "Bird Detected (Ignored)", (x1, y2 + 15), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 165, 0), 1)
                
                # 5. Handle Alerts with Temporal Smoothing
                if something_in_zone:
                    self.detection_persistence += 1
                else:
                    self.detection_persistence = 0 # Reset immediately if lost
                
                if self.detection_persistence >= self.persistence_threshold:
                    if not self.system_status['alarm_active']:
                        logger.info(f"Stable detection confirmed ({self.detection_persistence} frames). Triggering alarm.")
                        self.system_status['alarm_active'] = True
                        self.system_status['intrusion_count'] += 1
                        self.system_status['last_event'] = f"Intrusion (Vision) @ {time.strftime('%H:%M:%S')}"
                        if self.gpio_controller:
                            threading.Thread(target=self.gpio_controller.activate_buzzer).start()
                
                # 6. Encode
                ret, jpeg = cv2.imencode('.jpg', img)
                if ret:
                    new_frame = jpeg.tobytes()
                    with self.lock:
                        self.latest_frame = new_frame
                
                # Pace the loop (approx 25-30 fps)
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Frame Processor Error: {e}")
                time.sleep(0.5)

    def get_latest_frame(self):
        with self.lock:
            return self.latest_frame
