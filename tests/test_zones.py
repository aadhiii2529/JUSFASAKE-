import unittest
import requests
import json
import time
import threading
import sys
import os

# Add root to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.web.app import app

class TestZoneAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Flask app in a thread
        cls.flask_thread = threading.Thread(target=app.run, kwargs={'port': 5001, 'use_reloader': False})
        cls.flask_thread.daemon = True
        cls.flask_thread.start()
        time.sleep(1) # Wait for startup

    def test_add_zones(self):
        base_url = 'http://localhost:5001/api/zones'
        
        # Test Point
        point = {'type': 'point', 'x': 10, 'y': 20}
        r = requests.post(base_url, json=point)
        self.assertEqual(r.status_code, 200)
        
        # Test Rect
        rect = {'type': 'rect', 'x': 10, 'y': 20, 'w': 100, 'h': 50}
        r = requests.post(base_url, json=rect)
        self.assertEqual(r.status_code, 200)
        
        # Test Poly
        poly = {'type': 'poly', 'points': [{'x':1,'y':1}, {'x':10,'y':10}, {'x':1,'y':10}]}
        r = requests.post(base_url, json=poly)
        self.assertEqual(r.status_code, 200)
        
        # Verify Retrieval
        r = requests.get(base_url)
        zones = r.json()
        self.assertTrue(len(zones) >= 3)
        print(f"Verified {len(zones)} zones stored.")

if __name__ == '__main__':
    unittest.main()
