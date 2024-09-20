import cv2
import numpy as np
import time
from datetime import datetime
import os
from ultralytics import YOLO

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
    filename = f"{output_dir}/chicken_count_{count:02d}_date_{timestamp}.jpg"
    
    cv2.imwrite(filename, frame)
    print(f"Frame saved: {filename}")

def main():
    # Load the YOLOv8 model
    model = YOLO('model/yolov8n.pt')  # Replace with the path to your model

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

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # Spacebar pressed
            roi = process_frame(frame, mask)
            
            # Run YOLOv8 inference on the ROI, detecting only chickens (class 0)
            results = model.predict(source=roi, classes=[0])
            
            count = count_chickens(results)
            
            result_frame = draw_results(display_frame, count, results)
            cv2.imshow("Chicken Detection", result_frame)
            save_frame(result_frame, count)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()