from ultralytics import YOLO

model = YOLO("best.pt")
model.export(format="tflite", imgsz=320, dynamic=False, optimize=True)
