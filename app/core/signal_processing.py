try:
    import numpy as np
    from scipy.signal import butter, lfilter
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    import logging
    logging.getLogger(__name__).warning("Scipy/Numpy not found. Signal processing will be bypassed.")

class SignalProcessor:
    def __init__(self, lowcut, highcut, fs, order=5):
        self.lowcut = lowcut
        self.highcut = highcut
        self.fs = fs
        self.order = order
        if HAS_DEPS:
            self.b, self.a = self.butter_bandpass(lowcut, highcut, fs, order=order)

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        if not HAS_DEPS: return None, None
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def apply_filter(self, data):
        """
        Apply the Butterworth band-pass filter to the data.
        """
        if not HAS_DEPS:
            return data # Pass-through if no deps
        
        y = lfilter(self.b, self.a, data)
        return y
