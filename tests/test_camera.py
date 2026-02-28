import unittest
import cv2
import os
import time

class TestCamera(unittest.TestCase):
    def test_camera_mock(self):
        # Force mock mode by setting an invalid source
        os.environ['CAMERA_SOURCE'] = "999"
        from app.core import camera
        
        cam = camera.VideoCamera(source=999)
        frame = cam.get_frame()
        self.assertIsNotNone(frame)
        self.assertTrue(len(frame) > 0)
        print(f"Frame size: {len(frame)} bytes")

if __name__ == '__main__':
    unittest.main()
