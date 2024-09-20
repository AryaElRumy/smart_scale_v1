import cv2
from ultralytics import YOLO
import time

class YOLOv8VideoWriter:
    def __init__(self, model_path, input_video_path, output_video_path, device='cpu', conf=0.5, iou=0.7):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(input_video_path)
        self.device = device
        self.conf = conf
        self.iou = iou
        self.fps_filtered = 30
        self.tlast = time.time()

        # Get video properties
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        input_fps = self.cap.get(cv2.CAP_PROP_FPS)  # Get the FPS of the input video

        # Define the codec and create a VideoWriter object with the same FPS as the input video
        self.out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), input_fps, (width, height))

    def process_frame(self, frame):
        results = self.model.predict(frame, device=self.device, conf=self.conf, iou=self.iou, classes = 0)
        annotated_frame = results[0].plot()

        # Calculate and overlay FPS
        self.calculate_fps()
        cv2.putText(annotated_frame, f'FPS: {int(self.fps_filtered)}', (5, 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        return annotated_frame

    def calculate_fps(self):
        dt = time.time() - self.tlast
        fps = 1 / dt
        self.fps_filtered = self.fps_filtered * 0.9 + fps * 0.1
        self.tlast = time.time()

    def write_video(self):
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                break

            annotated_frame = self.process_frame(frame)
            self.out.write(annotated_frame)

        self.cap.release()
        self.out.release()

if __name__ == "__main__":
    model_path = "model/yolov8nChickenV1_ncnn_model/"
    input_video_path = "manual_val/Video2.mp4"
    output_video_path = "output_video/output_results_ncnn_i712700H.mp4"

    yolo_writer = YOLOv8VideoWriter(model_path, input_video_path, output_video_path)
    yolo_writer.write_video()
