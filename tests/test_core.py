import unittest
import numpy as np
import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.signal_processing import SignalProcessor
from app.core.inference import InferenceEngine

class TestCoreLogic(unittest.TestCase):
    def setUp(self):
        self.fs = 100
        self.processor = SignalProcessor(2.0, 15.0, self.fs)
        self.inference = InferenceEngine()

    def test_filter_shape(self):
        # Generate random signal
        data = np.random.randn(1000)
        filtered = self.processor.apply_filter(data)
        self.assertEqual(len(data), len(filtered))

    def test_inference_mock(self):
        # Silence
        silence = np.zeros(100)
        self.assertFalse(self.inference.predict(silence))

        # High energy signal (should trigger mock threshold)
        loud = np.random.randn(100) * 10 
        self.assertTrue(self.inference.predict(loud))

if __name__ == '__main__':
    unittest.main()
