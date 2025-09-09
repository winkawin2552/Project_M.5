import cv2 as cv
import numpy as np
# from libraries.l298n import L298N
# from RPi.GPIO import *
# setmode(BCM)

def white_detect(frame):
    try:
        blur = cv.GaussianBlur(frame, (5,5), 0)
        # --- Detect only white ---
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        mask = cv.inRange(hsv, lower_white, upper_white)
        white_only = cv.bitwise_and(blur, blur, mask=mask)
        return white_only
    except Exception as e:
        print("Error in white_detect:", e)
        return frame

def pos_white(binary_img):
    contours, hierarchy = cv.findContours(binary_img,
                                         cv.RETR_EXTERNAL,
                                         cv.CHAIN_APPROX_NONE)
    return contours

# motor1 = L298N([22, 27, 17])
# motor2 = L298N([24, 23, 25])

# speed = 50

# while 1:
        # motor1.setSpeed(speed, True)
        # motor2.setSpeed(speed, True)

def adjust_motor(store_dist, dist_mid = 151):
    store_dist = sorted(store_dist)
    print(store_dist)
    if len(store_dist) == 2:
        diff = abs(store_dist[0]) - abs(store_dist[1])
        print(f'Find two: {diff}')
    else:
        if store_dist[0] < 0:
            diff = dist_mid - abs(store_dist[0])
            print(f'Left: {diff}')
        else:
            diff = dist_mid - store_dist[0]
            print(f'Right: {diff}')
    pass

video_path = "my_video-3.mkv" 
cap = cv.VideoCapture(video_path)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

# ROI coordinates
y1, y2 = 140, 150
x1, x2 = 0, 320

mid = [160 ,144]
dist_mid = 140

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.resize(frame, (320, 240))

    cropped_frame = frame[y1:y2, x1:x2]

    processed = white_detect(cropped_frame)

    gray = cv.cvtColor(processed, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)

    contours = pos_white(thresh)
    store_dist = []
    for cnt in contours:
        M = cv.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            dist = cx - mid[0]
            store_dist.append(dist)
            cv.line(frame, mid, (cx, cy+140), (0,0,0), 2)
            cv.circle(frame, (cx, cy+ 140), 5, (255, 0, 0), -1)
    adjust_motor(store_dist, dist_mid)

    cv.circle(frame, mid, 5, (0,255,0), -1)
    cv.imshow('Processed ROI', frame)

    if cv.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()