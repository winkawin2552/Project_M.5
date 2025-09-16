from ultralytics import YOLO
import cv2

model = YOLO("best.torchscript")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

count_frame = 0
while True:
    ret, frame = cap.read()
    count_frame += 1
    if not ret:
        break
    if count_frame == 7:
        results = model.predict(frame)

        # draw annotated frame
        frame = results[0].plot()

        # print box info
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # bounding box coords
            conf = float(box.conf[0])              # confidence
            cls = int(box.cls[0])                  # class id
            label = model.names[cls]               # class name

            print(f"Label: {label}, Conf: {conf:.2f}, "
                  f"Box: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
            print(f'width {abs(x1- x2)}')

        count_frame = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
