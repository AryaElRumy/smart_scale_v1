import cv2
import yaml

class Camera:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.device_id = config['camera']['device_id']
        self.cap = None

    def initialize(self):
        self.cap = cv2.VideoCapture(self.device_id)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open camera with device ID {self.device_id}")

    def get_frame(self):
        if self.cap is None:
            raise ValueError("Camera is not initialized")
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to capture frame")
        return frame

    def get_dimensions(self):
        if self.cap is None:
            raise ValueError("Camera is not initialized")
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height

    def release(self):
        if self.cap is not None:
            self.cap.release()