import cv2
from ultralytics import YOLO
import time
from collections import defaultdict
import numpy as np

class ChickenTracker:
    def __init__(self, model_path, video_source=0, circle_radius=200, display=False, save_video=False, output_path="output.mp4"):
        self.model = YOLO(model_path)
        self.cap = self.initialize_camera(video_source)
        self.circle_center = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2, int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2)
        self.circle_radius = circle_radius
        self.track_history = defaultdict(list)
        self.circle_color = (0, 0, 255)
        self.circle_thickness = 2
        self.tlast = time.time()
        self.display = display
        self.save_video = save_video
        self.writer = self.initialize_writer(output_path) if save_video else None

    def initialize_camera(self, video_source):
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise Exception("Could not open video source")
        cap.set(cv2.CAP_PROP_FPS, 30)
        return cap

    def initialize_writer(self, output_path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        return writer

    def draw_circle(self, frame):
        cv2.circle(frame, self.circle_center, self.circle_radius, self.circle_color, self.circle_thickness)

    def update_track_history(self, track_id, bbox_center):
        track = self.track_history[track_id]
        track.append((float(bbox_center[0]), float(bbox_center[1])))
        if len(track) > 30:
            track.pop(0)
        return np.hstack(track).astype(np.int32).reshape((-1, 1, 2))

    def is_inside_circle(self, bbox_center):
        distance_to_center = np.linalg.norm(np.array(bbox_center) - np.array(self.circle_center))
        return distance_to_center <= self.circle_radius

    def process_frame(self, frame):
        results = self.model.track(frame, device='cpu', conf=0.8, iou=0.7, classes=0)
        count_inside_circle = 0

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                bbox_center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
                self.update_track_history(track_id, bbox_center)

                if self.is_inside_circle(bbox_center):
                    count_inside_circle += 1
                    if self.display:
                        cv2.circle(frame, (int(bbox_center[0]), int(bbox_center[1])), 5, (0, 255, 0), -1)

        return count_inside_circle

    def calculate_fps(self):
        dt = time.time() - self.tlast
        fps = 1 / dt
        self.tlast = time.time()
        return int(fps)

    def display_info(self, frame, fps, count_inside_circle):
        cv2.rectangle(frame, (0, 0), (150, 80), (0, 0, 0), -1)
        cv2.putText(frame, f'FPS: {fps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f'Count: {count_inside_circle}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            fps = self.calculate_fps()
            self.draw_circle(frame)
            count_inside_circle = self.process_frame(frame)
            self.display_info(frame, fps, count_inside_circle)

            if self.display:
                frame = cv2.resize(frame, (640, 640))
                cv2.imshow('Chicken Tracker', frame)
                if cv2.waitKey(1) == ord('q'):
                    break

            if self.save_video:
                self.writer.write(frame)

        self.cap.release()
        if self.save_video:
            self.writer.release()
        if self.display:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ChickenTracker(
        model_path="model/ChickenCounterV4.pt", 
        video_source="manual_val/Video2.mp4", 
        display=True, 
        save_video=False,  # Set this to True to save the video, False to disable saving
        output_path=""
    )
    tracker.run()