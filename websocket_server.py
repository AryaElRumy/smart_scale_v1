import asyncio
import json
from sanic import Sanic, Request, Websocket
from sanic.response import json as json_response, file
import paho.mqtt.client as mqtt
from queue import Queue
from threading import Thread
import os

app = Sanic("WebSocketMQTTServer")
connected_websockets = set()
message_queue = Queue()

# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_topic = "smart_scale/data"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    message_queue.put(msg.payload.decode())

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# WebSocket route
@app.websocket("/ws")
async def websocket(request: Request, ws: Websocket):
    connected_websockets.add(ws)
    try:
        async for msg in ws:
            # Here you can handle any incoming messages from the client if needed
            print(f"Received from client: {msg}")
    finally:
        connected_websockets.remove(ws)

# Broadcast function
async def broadcast(message):
    for ws in connected_websockets:
        await ws.send(message)

# Message processor
async def process_messages():
    while True:
        while not message_queue.empty():
            message = message_queue.get()
            try:
                data = json.loads(message)
                # Extract image path and create a URL
                image_path = data.get('image_path')
                if image_path:
                    # Assuming the image path is relative to the server's root
                    image_url = f"/images/{os.path.basename(image_path)}"
                    data['image_url'] = image_url
                await broadcast(json.dumps(data))
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {message}")
        await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

# Route to serve images
@app.route("/images/<filename:string>")
async def serve_image(request: Request, filename: str):
    return await file(f"output_image/{filename}")

# Start MQTT client
def start_mqtt_client():
    mqtt_client.connect("localhost", 1883, 60)  # Replace with your MQTT broker address
    mqtt_client.loop_forever()

# Setup before server starts
@app.listener('before_server_start')
def setup(app, loop):
    # Start MQTT client in a separate thread
    mqtt_thread = Thread(target=start_mqtt_client)
    mqtt_thread.start()
    
    # Start the message processing task
    app.add_task(process_messages())

# Cleanup after server stops
@app.listener('after_server_stop')
def cleanup(app, loop):
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)