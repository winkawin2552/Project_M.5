import cv2 as cv
import numpy as np
from libraries.l298n import L298N
from RPi.GPIO import *
from ultralytics import YOLO
import time
setmode(BCM)

model = YOLO("best.torchscript")
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

motorR = L298N([23, 24, 25]) 
motorL = L298N([27, 22, 17]) 

speed_default = 60

speedR = speed_default
speedL = speed_default

motorR.setSpeed(0, True)
motorL.setSpeed(0, True)

collect_error = []
start = 0

find_something = 1
def adjust_motor(store_dist, dist_mid = 151):

    global find_something
    global start

    store_dist = sorted(store_dist)
    speedR = speed_default
    speedL = speed_default
    try:
        if len(store_dist) == 4:
            diff = abs(store_dist[0]) - abs(store_dist[1])
            if diff < 0:
                collect_error.append([abs(diff), 0])
            else:
                collect_error.append([0, abs(diff)])
        else:
            if store_dist[0] < 0: # find only left
                diff = dist_mid - abs(store_dist[0])
                collect_error.append([abs(diff), 0])
            else: # find only right
                diff = dist_mid - store_dist[0]
                collect_error.append([0, abs(diff)])
        speedL += collect_error[0][0]
        speedR += collect_error[0][1]
        if len(collect_error) == 2:
            collect_error.pop(0)
        if speedR > 100:
            speedR = 90
            speedL -= 10
        if speedL > 100:
            speedL = 90
            speedR -= 10
    except:
        pass
    motorR.setSpeed(speedR * find_something * start, True)
    motorL.setSpeed(speedL * find_something * start, True)

def detect(frame):
    results = model.predict(frame, conf = 0.09)
    collect = dict()

    frame = results[0].plot()

    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()  
        conf = float(box.conf[0])             
        cls = int(box.cls[0])                  
        label = model.names[cls]
        collect[label] = [[x1, y1, x2, y2], conf, abs(x1-x2)]
    cv.imshow("frame", frame)
    print(collect)
    return collect          

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

# ROI coordinates
y1, y2 = 140, 150
x1, x2 = 0, 320

plus = 0 # 140
mid = [160 ,4 + plus]
dist_mid = 140

count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
#-------------------------------LANE DETECT--------------------------------------------------
    frame = cv.resize(frame, (320, 240))
    resize = cv.resize(frame, (160, 120))

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
            # cv.line(cropped_frame, mid, (cx, cy+plus), (0,0,0), 2)
            # cv.circle(cropped_frame, (cx, cy+ plus), 5, (255, 0, 0), -1)
    adjust_motor(store_dist, dist_mid)

    # cv.circle(cropped_frame, mid, 5, (0,255,0), -1)
#----------------------------------OBJECT DETECT----------------------------------------------
    count += 1
    if count == 7:
        find_something = 1
        describe = detect(frame)
        if not bool(start):
            motorR.setSpeed(0, True)
            motorL.setSpeed(0, True)
            if 'green' in list(describe.keys()):
                start = 1
        else:
            if len(describe.keys()) == 1:
                if list(describe.keys())[0] == "leeling":
                    if describe['leeling'][2] > 59: # 67
                        find_something = 0
                elif list(describe.keys())[0] == "stop":
                    if describe['stop'][2] > 22: # 20
                        find_something = 0

        count = 0
#---------------------------------------------------------------------------------------------
    # cv.imshow('Processed ROI', cropped_frame)

    if cv.waitKey(33) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
