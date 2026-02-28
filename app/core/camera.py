import threading
import time
import logging
import os
import random

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV or Numpy not found. Camera will run in MOCK mode.")

class VideoCamera:
    def __init__(self, source=None):
        self.source = source if source is not None else os.environ.get('CAMERA_SOURCE', 0)
        self.video = None
        
        if HAS_CV2:
            # If source is a string but looks like an int, convert it
            if isinstance(self.source, str) and self.source.isdigit():
                self.source = int(self.source)
            
            try:
                self.video = cv2.VideoCapture(self.source)
                if not self.video.isOpened():
                    logger.warning(f"Could not open video source {self.source}.")
                    self.video = None
            except Exception as e:
                logger.error(f"Error opening camera: {e}")
                self.video = None
        
        self.lock = threading.Lock()

    def __del__(self):
        if self.video:
            self.video.release()

    def get_frame(self):
        """Return the current frame encoded as JPEG bytes."""
        with self.lock:
            if HAS_CV2 and self.video and self.video.isOpened():
                success, image = self.video.read()
                if success:
                    ret, jpeg = cv2.imencode('.jpg', image)
                    return jpeg.tobytes()
            
            return self._get_mock_frame()

    def update_source(self, new_source):
        """Update the video source dynamically."""
        with self.lock:
            # Clean up the input source
            if isinstance(new_source, str):
                new_source = new_source.strip()
                if not new_source: new_source = '0'
            
            logger.info(f"Updating camera source to: {new_source}")
            self.source = new_source
            
            if self.video:
                self.video.release()
                self.video = None
            
            if HAS_CV2:
                # If source is a string but looks like an int, convert it
                if isinstance(self.source, str) and self.source.isdigit():
                    self.source = int(self.source)
                
                try:
                    self.video = cv2.VideoCapture(self.source)
                    if not self.video.isOpened():
                        logger.warning(f"Could not open video source {self.source}.")
                        self.video = None
                    else:
                        logger.info(f"Successfully opened video source {self.source}")
                except Exception as e:
                    logger.error(f"Error opening camera: {e}")
                    self.video = None

    def _get_mock_frame(self):
        # Generate a mock JPEG frame (random noise or solid color)
        # Without cv2, we can't easily encode text on image. 
        # So we'll return a pre-defined simple JPEG header or a hardcoded standard "missing" image bytes
        # Or better: generate simple noise using basic python structs if needed, but that's hard to encode to JPG without libs.
        
        # If we have cv2 but camera failed:
        if HAS_CV2:
            img = np.zeros((300, 600, 3), dtype=np.uint8)
            # Add static noise
            noise = np.random.randint(0, 30, (300, 600, 3), dtype=np.uint8)
            img = cv2.add(img, noise)
            
            # Simple "No Signal" bars look
            cv2.rectangle(img, (0, 0), (600, 40), (40, 40, 40), -1)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, 'NO SIGNAL - CAMERA OFFLINE', (120, 150), font, 0.9, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(img, 'RUNNING IN SIMULATION MODE', (160, 180), font, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
            
            # Add moving live timestamp
            t_str = time.strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(img, f"LIVE FEED: {t_str}", (10, 30), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            # Signal bar
            cv2.putText(img, "SIGNAL: [|||||   ] 60%", (400, 30), font, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
            
            ret, jpeg = cv2.imencode('.jpg', img)
            return jpeg.tobytes()
            
        # Absolute fallback if no CV2: Return a tiny 1x1 gray pixel jpeg or similar
        # 1x1 pixel gray jpeg hex
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\xbf\xff\xd9'
