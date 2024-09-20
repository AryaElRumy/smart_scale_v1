import paho.mqtt.client as mqtt

# MQTT Broker details
broker = 'localhost'
port = 1883
topic = 'smart_scale/weight'

# Create a client instance
client = mqtt.Client()

# Connect to the broker
client.connect(broker, port, 60)

# Loop to get user input and publish it to the MQTT broker
try:
    while True:
        weight = input("Enter the weight data to publish: ")
        
        client.publish(topic, weight)
        print(f"Published: {weight} to topic: {topic}")

except KeyboardInterrupt:
    print("MQTT publishing stopped.")

finally:
    # Disconnect the client when done
    client.disconnect()
