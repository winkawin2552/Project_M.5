import cv2 as cv
import numpy as np
from libraries.l298n import L298N
from RPi.GPIO import *
setmode(BCM)

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

motorR = L298N([22, 27, 17])
motorL = L298N([24, 23, 25])

speed_default = 60

speedR = speed_default
speedL = speed_default

collect_error = []

def adjust_motor(store_dist, dist_mid = 151):
    store_dist = sorted(store_dist)
    print(store_dist)
    speedR = speed_default
    speedL = speed_default
    try:
        if len(store_dist) == 4:
            diff = abs(store_dist[0]) - abs(store_dist[1])
            if diff < 0:
                collect_error.append([abs(diff), 0])
            else:
                collect_error.append([0, abs(diff)])
            print(f'Find two: {diff}')
        else:
            if store_dist[0] < 0: # find only left
                diff = dist_mid - abs(store_dist[0])
                collect_error.append([abs(diff), 0])
                print(f'Left: {diff}')
            else: # find only right
                diff = dist_mid - store_dist[0]
                collect_error.append([0, abs(diff)])
                print(f'Right: {diff}')
        speedL += collect_error[0][0]
        speedR += collect_error[0][1]
        if len(collect_error) == 6:
            collect_error.pop(0)
        print(len(collect_error))
        print(f'left: {collect_error[0][0]}, right: {collect_error[0][1]}')
        if speedR > 100:
            speedR = 100
            speedL -= 10
        if speedL > 100:
            speedL = 100
            speedR -= 10
        print(f"speedR: {speedR}, speedL: {speedL}")
    except:
        pass
    motorR.setSpeed(speedR, True)
    motorL.setSpeed(speedL, True)

video_path = "my_video-3.mkv" 
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

# ROI coordinates
y1, y2 = 140, 150
x1, x2 = 0, 320

plus = 0 # 140
mid = [160 ,4 + plus]
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
            cv.line(cropped_frame, mid, (cx, cy+plus), (0,0,0), 2)
            cv.circle(cropped_frame, (cx, cy+ plus), 5, (255, 0, 0), -1)
    adjust_motor(store_dist, dist_mid)

    cv.circle(cropped_frame, mid, 5, (0,255,0), -1)
    cv.imshow('Processed ROI', cropped_frame)

    if cv.waitKey(33) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
