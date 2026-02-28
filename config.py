import os

class Config:
    MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'seismic/data')
    
    # Signal Processing
    SAMPLING_RATE = 100  # Hz
    FILTER_LOWCUT = 2.0
    FILTER_HIGHCUT = 15.0
    
    # GPIO
    BUZZER_PIN = 18
    
    # Web
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
