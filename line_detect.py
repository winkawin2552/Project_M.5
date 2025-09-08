# from libraries.l298n import L298N
# from RPi.GPIO import *
# setmode(BCM)
import time
import cv2 as cv
import numpy as np
 
def line_detect(frame):
    canny = cv.Canny(frame,0,300)
    pts = np.array([[0,1080], [0, 500], [1920, 500], [1920, 1080]], np.int32)
    roi = np.zeros_like(canny)
    cv.fillPoly(roi, [pts],[255,255,255])
    roadblack = cv.bitwise_and(canny, canny,mask=roi)
    final = cv.bitwise_and(canny,canny,mask=roadblack)
    lines = cv.HoughLinesP(final, 1, np.pi / 180, 120, minLineLength=100, maxLineGap=20)
 
    frame_line = frame.copy()    
   
    return frame_line, lines
 
 
def average_line(lines):
    left = []
    right = []
    for i in lines:
        x1, y1, x2, y2 = i[0]
        slope = (x1 - x2)/(y1-y2)
        if slope < 0 :
            right.append(i)
        else:
            left.append(i)
    try:
        left = list(map(int, np.average(left, axis=0)[0]))
        right = list(map(int, np.average(right, axis=0)[0]))
    except:
        pass
    return left, right
 
def make_point(left, right, Y = 1070):
    Y = Y
    try:
        lx1, ly1, lx2, ly2 = left
        rx1, ry1, rx2, ry2 = right
 
        LX = int((Y - (ly1 - ((ly1-ly2)/(lx1-lx2))*lx1))/((ly1-ly2)/(lx1-lx2)))
        RX = int((Y - (ry1 - ((ry1-ry2)/(rx1-rx2))*rx1))/((ry1-ry2)/(rx1-rx2)))
    except:
        LX = 0
        RX = 0
    return LX, RX
 
def diff(pos1, pos2, center):
    lenght1 = np.sqrt((pos1[0] - center[0])**2 + (pos1[1] - center[1])**2)
    lenght2 = np.sqrt((pos2[0] - center[0])**2 + (pos2[1] - center[1])**2)
    diff = lenght1 - lenght2
    return diff

# motor1 = L298N([22, 27, 17])
# motor2 = L298N([24, 23, 25])

speed = 50

# while 1:
        # motor1.setSpeed(speed, True)
        # motor2.setSpeed(speed, True)

cap = cv.VideoCapture(2)
previous = [720, 240]
while 1:
    Y = 1050
    ret, frame = cap.read()

    frame, lines = line_detect(frame)
    coordinate = average_line(lines=lines)
    left, right = average_line(lines)
    LX,RX = make_point(left, right)
    if LX == 0 and RX == 0:
        LX,RX = previous
    else:
        previous = [LX, RX]
    previous = [LX, RX]
    error = diff([LX, Y], [RX, Y], (int(1920/2), 1080))
    cv.circle(frame, (LX, Y), 15, (0,0,255),-1)
    cv.circle(frame, (RX, Y), 15, (0,0,255),-1)
    cv.circle(frame, (int(1920/2), 1080), 15, (255,0,0),-1)
 
    frame = cv.resize(frame, None, fx= 0.7, fy=0.7)
    
    cv.imshow('frame', frame)
