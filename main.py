import cv2 as cv
import numpy as np

def blank_space(pts, frame):
    roi = np.zeros_like(frame)
    cv.fillPoly(roi, [pts],[255,255,255])
    roadblack = cv.bitwise_and(frame, frame,mask=roi)
    final = cv.bitwise_and(frame,frame,mask=roadblack)
    return final

def line_detect(frame):
    try:
        blur = cv.GaussianBlur(frame, (5,5), 0)
        gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
        sobelY = cv.Sobel(gray, cv.CV_64F, 0, 1, ksize=3)
        lap = cv.Laplacian(sobelY, cv.CV_64F)
        lap = cv.convertScaleAbs(lap)
        canny = cv.Canny(lap, 50, 150)
        kernel = np.ones((5,5), np.uint8)
        closed = cv.morphologyEx(canny, cv.MORPH_CLOSE, kernel)
        opened = cv.morphologyEx(closed, cv.MORPH_OPEN, kernel)

        # ROI mask
        pts = np.array([[0,480],[640, 480], [640, 240],[0, 240]],  np.int32)
        final = blank_space(pts, opened)
        pts = np.array([[0, 240], [320, 240], [320, 480], [0, 480]],  np.int32)
        final = blank_space(pts, final)

        lines = cv.HoughLinesP(final, 1, np.pi / 180, 120, minLineLength=100, maxLineGap=20)
        # draw detected lines
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    except:
        lines = None 
    return frame, lines

def average_left_line(lines):
    try:
        left = list(map(int, np.average(lines, axis=0)[0]))
    except:
        left = None
    return left

def make_left_point(left, Y = 360):
    try:
        lx1, ly1, lx2, ly2 = left
        if lx1 == lx2:
            return 0
        LX = int((Y - (ly1 - ((ly1-ly2)/(lx1-lx2))*lx1))/((ly1-ly2)/(lx1-lx2)))
    except:
        LX = 0
    return LX


video_path = "my_video-3.mkv" 
cap = cv.VideoCapture(video_path)

previous = 320
Y = 300

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame, lines = line_detect(frame)
    left = average_left_line(lines)
    try:
        cv.line(frame, [left[0], left[1]], [left[2], left[3]], (0,0,255), 5)
    except:
        pass
    LX = make_left_point(left, Y)

    if LX == 0:
        LX = previous
    else:
        previous = LX
    mid_point = [320, Y]
    cv.circle(frame, mid_point, 10, (255,0,0), -1)
    try:
        radius = 10
        cv.circle(frame, (LX, Y), radius, (0,0,255), -1)
        cv.line(frame, (LX, Y), mid_point, (0,0,0), 2)
        dist = np.linalg.norm(np.array((LX, Y)) - np.array(mid_point))
        cv.putText(frame, f'Dist: {dist:.2f}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    except:
        pass
    try:
        ratio = 0.7
        frame = cv.resize(frame, None, fx=ratio, fy=ratio)
    except:
        pass

    cv.imshow('frame', frame)

    if cv.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
