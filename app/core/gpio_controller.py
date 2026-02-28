import os
import time
import logging

# Check if running on Raspberry Pi
IsRaspberryPi = False
try:
    import RPi.GPIO as GPIO
    IsRaspberryPi = True
except ImportError:
    pass

class GPIOController:
    def __init__(self, pin):
        self.pin = pin
        self.logger = logging.getLogger(__name__)
        
        if IsRaspberryPi:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)
            self.logger.info(f"GPIO initialized on pin {self.pin}")
        else:
            self.logger.warning("RPi.GPIO not found. Running in MOCK mode.")

    def activate_buzzer(self, duration=1.0):
        """Turn on the buzzer for a specified duration."""
        self.logger.info(f"Adding output [GPIO {self.pin}]: ON (!!! HIGH DB BUZZER ACTIVATED !!!)")
        if IsRaspberryPi:
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.pin, GPIO.LOW)
            self.logger.info(f"Adding output [GPIO {self.pin}]: OFF")
        else:
            # Mock behavior
            time.sleep(duration)
            self.logger.info(f"Adding output [GPIO {self.pin}]: OFF (Mock duration complete)")

    def deactivate_buzzer(self):
        """Turn off the buzzer."""
        self.logger.info(f"Adding output [GPIO {self.pin}]: OFF")
        if IsRaspberryPi:
            GPIO.output(self.pin, GPIO.LOW)

    def cleanup(self):
        if IsRaspberryPi:
            GPIO.cleanup()
