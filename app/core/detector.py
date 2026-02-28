import logging
import random

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
    logger.warning("Ultralytics/YOLO not found. Using MOCK detector.")

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = None
        if HAS_YOLO:
            try:
                # Load a pretrained YOLOv8n model
                self.model = YOLO(model_path)
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                
    def detect(self, frame):
        """
        Run inference on a frame (bytes or numpy array).
        Returns list of detections: {'class': 'person', 'bbox': [x1, y1, x2, y2], 'conf': 0.9}
        """
        results = []
        
        if self.model:
            # YOLO accepts numpy array (which we get from cv2)
            # frame needs to be decoded from jpeg bytes if raw bytes passed?
            # Assuming caller passes numpy array. If bytes, we need to decode.
            import cv2
            import numpy as np
            
            if isinstance(frame, bytes):
                nparr = np.frombuffer(frame, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = frame
                
            try:
                # Run inference
                # stream=True for memory efficiency, but we just want one frame result
                # verbose=False to reduce logs
                prediction = self.model(img, verbose=False, conf=0.5)[0] # Increased default confidence threshold
                
                for box in prediction.boxes:
                    cls_id = int(box.cls[0])
                    if cls_id in self.model.names:
                        class_name = self.model.names[cls_id]
                        # Filter ONLY person - birds are now completely disabled as requested
                        if class_name == 'person':
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            conf = float(box.conf[0])
                            results.append({
                                'class': class_name,
                                'bbox': [x1, y1, x2, y2],
                                'conf': conf
                            })
            except Exception as e:
                logger.error(f"Inference error: {e}")
                
        else:
            # Mock Detection
            # Only detect 'person' occasionally to avoid bird confusion
            if random.random() < 0.05: # Reduced frequency for stability
                # Mock coords within 600x300 canvas
                x = random.randint(0, 500)
                y = random.randint(0, 200)
                results.append({
                    'class': 'person',
                    'bbox': [x, y, x+50, y+100],
                    'conf': 0.92
                })
                
        return results
