import cv2
from ultralytics import YOLO
import time

class YOLOv8Inference:
    def __init__(self, model_path, video_path,device = 'cpu', conf=0.8, iou=0.7):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(video_path)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.device = device
        self.conf = conf
        self.iou = iou
        self.fps_filtered = 30
        self.tlast = time.time()

    def process_frame(self, frame):
        results = self.model.predict(frame, device=self.device, conf=self.conf, iou=self.iou, classes =0)
        return results[0].plot()

    def display_frame(self, frame):
        resized_frame = cv2.resize(frame, (self.frame_width//2, self.frame_height//2))
        cv2.putText(resized_frame, f'FPS: {int(self.fps_filtered)}', (5, 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("YOLOv8 Inference", resized_frame)

    def calculate_fps(self):
        dt = time.time() - self.tlast
        fps = 1 / dt
        self.fps_filtered = self.fps_filtered * 0.9 + fps * 0.1
        self.tlast = time.time()

    def run_inference(self):
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                break

            self.calculate_fps()
            annotated_frame = self.process_frame(frame)
            self.display_frame(annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    model_path = "model/ChickenCounterV4_ncnn_model/"
    video_path = "manual_val/Video2.mp4"
    yolo_inference = YOLOv8Inference(model_path, video_path)
    yolo_inference.run_inference()