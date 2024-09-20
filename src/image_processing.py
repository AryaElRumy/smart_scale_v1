import cv2
import numpy as np
import yaml

class ImageProcessor:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.radius_fraction = config['roi']['radius_fraction']

    def create_circular_mask(self, frame_shape, center, radius):
        #this method create a mask from frame to be processed
        Y, X = np.ogrid[:frame_shape[0], :frame_shape[1]]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
        mask = dist_from_center <= radius
        return mask

    def draw_roi(self, frame, center, radius):
        #this method display the original frame with ROI
        frame_with_roi = frame.copy()
        cv2.circle(frame_with_roi, center, radius, (0, 255, 0), 2)
        return frame_with_roi

    def get_roi(self, frame, mask):
        #circle frame
        roi = frame.copy()
        roi[~mask] = 0
        return roi

    def draw_results(self, frame, count, results):
        result_frame = frame.copy()
        cv2.putText(result_frame, f"Chicken Count: {count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        for box in results[0].boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(result_frame, (center_x, center_y), 5, (0, 0, 255), -1)
        
        return result_frame

    def get_roi_params(self, frame_width, frame_height):
        center = (frame_width // 2, frame_height // 2)
        radius = int(min(frame_width, frame_height) * self.radius_fraction)
        return center, radius