import cv2
from ultralytics import YOLO
import numpy as np

class ChickenTrackerOnDemand:
    def __init__(self, model_path, video_source=0, circle_radius=200, display=False, save_video=False, output_path="output.mp4"):
        self.model = YOLO(model_path)
        self.cap = self.initialize_camera(video_source)
        self.circle_center = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2, int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2)
        self.circle_radius = circle_radius
        self.display = display
        self.save_video = save_video
        self.writer = self.initialize_writer(output_path) if save_video else None

    def initialize_camera(self, video_source):
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise Exception("Could not open video source")
        return cap

    def initialize_writer(self, output_path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    def extract_roi(self, frame):
        x_center, y_center = self.circle_center
        radius = self.circle_radius
        x_start = max(0, x_center - radius)
        y_start = max(0, y_center - radius)
        x_end = min(frame.shape[1], x_center + radius)
        y_end = min(frame.shape[0], y_center + radius)
        return frame[y_start:y_end, x_start:x_end], (x_start, y_start)

    def process_frame(self, frame):
        roi, (x_offset, y_offset) = self.extract_roi(frame)
        results = self.model.track(roi, device='cpu', conf=0.5, iou=0.7, classes=0)
        count_inside_circle = 0

        if results[0].boxes.id is not None:
            for box in results[0].boxes.xyxy.cpu().numpy():
                bbox_center = ((box[0] + box[2]) / 2 + x_offset, (box[1] + box[3]) / 2 + y_offset)
                if self.is_inside_circle(bbox_center):
                    count_inside_circle += 1

        return count_inside_circle

    def is_inside_circle(self, bbox_center):
        return np.linalg.norm(np.array(bbox_center) - np.array(self.circle_center)) <= self.circle_radius

    def display_info(self, frame, count_inside_circle):
        cv2.rectangle(frame, (0, 0), (150, 50), (0, 0, 0), -1)
        cv2.putText(frame, f'Count: {count_inside_circle}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            key = cv2.waitKey(1)
            if key == ord(' '):  # Process frame when spacebar is pressed
                count_inside_circle = self.process_frame(frame)
                self.display_info(frame, count_inside_circle)
                print(f"Chickens inside the circle: {count_inside_circle}")  # Print the count
            elif key == ord('q'):
                break

            if self.display:
                cv2.circle(frame, self.circle_center, self.circle_radius, (0, 0, 255), 2)
                frame = cv2.resize(frame, (640, 640))
                cv2.imshow('Chicken Tracker', frame)

            if self.save_video:
                self.writer.write(frame)

        self.cap.release()
        if self.save_video:
            self.writer.release()
        if self.display:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ChickenTrackerOnDemand(
        model_path="model/yolov8nChickenV1_saved_model/yolov8nChickenV1_float32.tflite", 
        video_source="manual_val/Video2.mp4", 
        display=True, 
        save_video=False  # Set this to True if you want to save the video results
    )
    tracker.run()