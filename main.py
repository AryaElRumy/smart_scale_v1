import cv2
from datetime import datetime
from src.camera import Camera
from src.image_processing import ImageProcessor
from src.mqtt_handler import MQTTHandler
from src.detector import Detector
from src.data_handler import DataHandler
from src.mysql_handler import MYSQLHandler

def main():
    camera = Camera()
    image_processor = ImageProcessor()
    mqtt_handler = MQTTHandler()
    detector = Detector()
    data_handler = DataHandler()
    mysql_handler = MYSQLHandler()

    camera.initialize()
    mqtt_handler.connect(mqtt_handler.topic_weight)

    frame_width, frame_height = camera.get_dimensions()
    center, radius = image_processor.get_roi_params(frame_width, frame_height)
    mask = image_processor.create_circular_mask((frame_height, frame_width), center, radius)

    while True:
        frame = camera.get_frame()
        display_frame = image_processor.draw_roi(frame, center, radius)
        display_frame = cv2.resize(display_frame, (frame_width//2, frame_height//2))
        cv2.imshow("Chicken Detection", display_frame)

        if mqtt_handler.trigger_processing:
            time_triggered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            roi = image_processor.get_roi(frame, mask)
            results = detector.detect(roi)
            count = detector.count_chickens(results)

            if count > 0:
                result_frame = image_processor.draw_results(display_frame, count, results)
                cv2.imshow("Chicken Detection", result_frame)
                image_path = data_handler.save_frame(result_frame, count, mqtt_handler.current_weight)
                mqtt_handler.publish_data(time_triggered, mqtt_handler.current_weight, count, image_path)
                mysql_handler.log_detection(time_triggered, mqtt_handler.current_weight, count, image_path)
            else:
                print("No chickens detected. Skipping data saving and publishing.")

            mqtt_handler.reset_trigger()

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    mqtt_handler.disconnect()
    mysql_handler.close()

if __name__ == "__main__":
    main()