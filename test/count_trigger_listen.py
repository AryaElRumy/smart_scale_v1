import cv2
import numpy as np
import time
from datetime import datetime
import os
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import json

# Constants
THRESHOLD_WEIGHT = 10
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC_WEIGHT = 'smart_scale/weight'
MQTT_TOPIC_DATA = 'smart_scale/data'

# Initialize global variables
trigger_processing = False
is_processing = False
current_weight = 0.0

def initialize_camera():
    return cv2.VideoCapture(0)

def create_circular_mask(frame_shape, center, radius):
    Y, X = np.ogrid[:frame_shape[0], :frame_shape[1]]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    mask = dist_from_center <= radius
    return mask

def draw_roi(frame, center, radius):
    cv2.circle(frame, center, radius, (0, 255, 0), 2)
    return frame

def process_frame(frame, mask):
    roi = frame.copy()
    roi[~mask] = 0
    return roi

def count_chickens(results):
    return len(results[0].boxes)

def draw_results(frame, count, results):
    cv2.putText(frame, f"Chicken Count: {count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Draw points on the center of detected chickens
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box[:4])
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Red dot
    
    return frame

def save_frame(frame, count):
    output_dir = "output_image"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{output_dir}/chicken_count_{count:02d}_date_{timestamp}_weight_{current_weight}.jpg"
    
    cv2.imwrite(filename, frame)
    print(f"Frame saved: {filename}")
    return filename

def publish_data(client, weight, count, image_path):
    average_weight = weight/count
    data = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_weight": weight,
        "total_count": count,
        "average_weight": average_weight,
        "image_path": image_path
    }
    client.publish(MQTT_TOPIC_DATA, json.dumps(data))
    print(f"Published data: {data}")

def on_message(client, userdata, message):
    global trigger_processing
    global current_weight
    global is_processing

    try:
        weight = float(message.payload.decode())
        print(f"Received weight: {weight}")
        if weight > THRESHOLD_WEIGHT and not is_processing:
            current_weight = weight
            trigger_processing = True
    except ValueError:
        print("Error decoding weight")

def main():
    global trigger_processing
    global current_weight
    global is_processing

    # Load the YOLOv8 model
    model = YOLO('model/yolov8n.pt')  # Replace with the path to your model

    # Initialize MQTT client
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC_WEIGHT)
    client.loop_start()

    cap = initialize_camera()
    
    # Define ROI parameters
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    center = (frame_width // 2, frame_height // 2)
    radius = min(frame_width, frame_height) // 4
    
    mask = create_circular_mask((frame_height, frame_width), center, radius)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = draw_roi(frame.copy(), center, radius)
        display_frame = cv2.resize(display_frame, (frame_width//2, frame_height//2))
        cv2.imshow("Chicken Detection", display_frame)

        if trigger_processing and not is_processing:
            is_processing = True
            roi = process_frame(frame, mask)
            
            # Run YOLOv8 inference on the ROI, detecting only chickens (class 0)
            results = model.predict(source=roi, classes=[0], conf = 0.7, iou=0.3)
            
            count = count_chickens(results)
            
            if count > 0:
                result_frame = draw_results(display_frame, count, results)
                cv2.imshow("Chicken Detection", result_frame)
                image_path = save_frame(result_frame, count)
                
                # Publish JSON data
                publish_data(client, current_weight, count, image_path)
            else:
                print("No chickens detected. Skipping data saving and publishing.")

            # Reset the trigger and processing flag
            trigger_processing = False
            is_processing = False

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    client.loop_stop()

if __name__ == "__main__":
    main()