import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# --- Webcam ---
cap = cv.VideoCapture(2)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)

root = tk.Tk()
root.title("White Color Calibration")

sliders = {}

def white_detect(frame, lower_white, upper_white):
    blur = cv.GaussianBlur(frame, (5,5), 0)
    hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

    mask = cv.inRange(hsv, lower_white, upper_white)
    white_only = cv.bitwise_and(blur, blur, mask=mask)

    # morphology cleanup
    kernel = np.ones((5,5), np.uint8)
    white_only = cv.morphologyEx(white_only, cv.MORPH_CLOSE, kernel)
    return white_only

def update_frame():
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv.resize(frame, (320, 240))

    # Get slider values
    l_h = sliders["Low H"].get()
    h_h = sliders["High H"].get()
    l_s = sliders["Low S"].get()
    h_s = sliders["High S"].get()
    l_v = sliders["Low V"].get()
    h_v = sliders["High V"].get()

    lower_white = np.array([l_h, l_s, l_v])
    upper_white = np.array([h_h, h_s, h_v])

    result = white_detect(frame, lower_white, upper_white)

    # Stack original + mask
    stacked = np.hstack((frame, result))

    # Convert to Tkinter-compatible image
    img = cv.cvtColor(stacked, cv.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)

    lbl.imgtk = imgtk
    lbl.configure(image=imgtk)

    root.after(30, update_frame)

def print_values():
    l_h = sliders["Low H"].get()
    h_h = sliders["High H"].get()
    l_s = sliders["Low S"].get()
    h_s = sliders["High S"].get()
    l_v = sliders["Low V"].get()
    h_v = sliders["High V"].get()
    print("Lower HSV:", [l_h, l_s, l_v])
    print("Upper HSV:", [h_h, h_s, h_v])

# --- Sliders ---
frame_controls = ttk.Frame(root)
frame_controls.pack(side="left", padx=10)

slider_params = [
    ("Low H", 0, 180, 0),
    ("High H", 0, 180, 180),
    ("Low S", 0, 255, 0),
    ("High S", 0, 255, 40),
    ("Low V", 0, 255, 200),
    ("High V", 0, 255, 255),
]

for text, frm, to, val in slider_params:
    lbl_s = ttk.Label(frame_controls, text=text)
    lbl_s.pack()
    sliders[text] = tk.Scale(frame_controls, from_=frm, to=to, orient="horizontal", length=200)
    sliders[text].set(val)
    sliders[text].pack()

# --- Video Display ---
lbl = ttk.Label(root)
lbl.pack(side="right")

# --- Button to print values ---
btn = ttk.Button(frame_controls, text="Print Values", command=print_values)
btn.pack(pady=10)

update_frame()
root.mainloop()

cap.release()
cv.destroyAllWindows()
