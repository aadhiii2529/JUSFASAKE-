import sys
import os

sys.path.append(os.path.abspath('.'))

try:
    from app.core.camera import VideoCamera
    print("VideoCamera import OK")
    from app.core.detector import ObjectDetector
    print("ObjectDetector import OK")
    from app.core.geometry import is_box_in_zone
    print("is_box_in_zone import OK")
    import cv2
    print("cv2 import OK")
    import numpy as np
    print("numpy import OK")
    import shapely
    print("shapely import OK")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
