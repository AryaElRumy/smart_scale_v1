import os
import cv2
from datetime import datetime
import yaml

class DataHandler:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.output_dir = config['output']['directory']
        os.makedirs(self.output_dir, exist_ok=True)

    def save_frame(self, frame, count, weight):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.output_dir}/chicken_count_{count:02d}_date_{timestamp}_weight_{weight:.2f}.jpg"
        
        cv2.imwrite(filename, frame)
        print(f"Frame saved: {filename}")
        return filename