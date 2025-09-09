import cv2 as cv
import numpy as np

def white_detect(frame):
    try:
        blur = cv.GaussianBlur(frame, (5,5), 0)
        # --- Detect only white ---
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        lower_white = np.array([0,0,200])
        upper_white = np.array([180, 40, 255])
        mask = cv.inRange(hsv, lower_white, upper_white)
        white_only = cv.bitwise_and(blur, blur, mask=mask)

    except:
        pass
    return white_only


video_path = "my_video-3.mkv" 
cap = cv.VideoCapture(2)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

previous = 320
Y = 120

# Define your ROI coordinates (y1:y2, x1:x2)
y1, y2 = 140, 150
x1, x2 = 0, 320

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.resize(frame, (320, 240))

    # --- Crop the frame first ---
    cropped_frame = frame[y1:y2, x1:x2]

    # Process only the cropped part
    processed = white_detect(cropped_frame)

    cv.imshow('frame', processed)

    if cv.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

