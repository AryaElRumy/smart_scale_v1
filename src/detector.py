from ultralytics import YOLO
import yaml

class Detector:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.model_path = config['yolo']['model_path']
        self.conf_threshold = config['yolo']['conf_threshold']
        self.iou_threshold = config['yolo']['iou_threshold']
        self.classes = config['yolo']['classes']

        self.model = YOLO(self.model_path)

    def detect(self, frame):
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=self.classes
        )
        return results

    def count_chickens(self, results):
        return len(results[0].boxes)