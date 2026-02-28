import unittest
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.detector import ObjectDetector

class TestDetector(unittest.TestCase):
    def test_detector_init(self):
        detector = ObjectDetector()
        self.assertIsNotNone(detector)

    def test_detection_mock_or_real(self):
        detector = ObjectDetector()
        # Create a blank image 640x480x3
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Run detection
        results = detector.detect(img)
        
        # Valid results should be a list
        self.assertIsInstance(results, list)
        
        # If mock is active, it might be empty or randomized. 
        # Just check structure if not empty
        if len(results) > 0:
            det = results[0]
            self.assertIn('class', det)
            self.assertIn('bbox', det)
            self.assertIn('conf', det)

if __name__ == '__main__':
    unittest.main()
