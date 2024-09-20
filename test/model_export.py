from ultralytics import YOLO

model = YOLO("model/yolov8nChickenV1.pt")
model.export(format = 'tflite')