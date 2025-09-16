import cv2 as cv
cap = cv.VideoCapture(2)
ratio = 2
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320/ratio)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240/ratio)

while 1:
    ret, frame = cap.read()
    if ret:
        cv.imshow('frame', frame)
        key = cv.waitKey(33)
        if key == ord('q'):
            break
    else:
        break

cap.release()
cv.destroyAllWindows()