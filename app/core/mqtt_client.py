import paho.mqtt.client as mqtt
import logging
import json

class MQTTClient:
    def __init__(self, broker, port, topic, on_message_callback, on_connect_callback=None):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic = topic
        self.on_message_callback = on_message_callback
        self.on_connect_callback = on_connect_callback
        self.logger = logging.getLogger(__name__)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info(f"Connected to MQTT Broker @ {self.broker}:{self.port}")
            client.subscribe(self.topic)
            if self.on_connect_callback:
                self.on_connect_callback()
        else:
            self.logger.error(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            # self.logger.debug(f"Received message on {msg.topic}: {payload}")
            self.on_message_callback(payload)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def start(self):
        self.logger.info(f"Connecting to {self.broker}...")
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"Could not connect to MQTT Broker: {e}")
            raise e

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
