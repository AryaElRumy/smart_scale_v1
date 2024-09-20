import paho.mqtt.client as mqtt
import yaml
import json
from datetime import datetime

class MQTTHandler:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.broker = config['mqtt']['broker']
        self.port = config['mqtt']['port']
        self.topic_weight = config['mqtt']['topic_weight']
        self.topic_data = config['mqtt']['topic_data']
        self.threshold_weight = config['threshold']['weight']

        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.current_weight = 0.0
        self.trigger_processing = False

    def connect(self, subscribe_topic):
        self.client.connect(self.broker, self.port, 60)
        self.client.subscribe(subscribe_topic)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()

    def on_message(self, client, userdata, message):
        try:
            data = float(message.payload.decode())
            print(f"Received data {data}")
            if data > self.threshold_weight:
                self.current_weight = data
                self.trigger_processing = True
        except ValueError:
            print("Error decoding weight")

    def publish_data(self, datetime, weight, count, image_path):
        average_weight = weight / count if count > 0 else 0
        data = {
            "datetime": datetime,
            "total_weight": weight,
            "total_count": count,
            "average_weight": average_weight,
            "image_path": image_path
        }
        self.client.publish(self.topic_data, json.dumps(data))
        print(f"Published data: {data}")

    def reset_trigger(self):
        self.trigger_processing = False