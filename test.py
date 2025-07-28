import mss
import pygetwindow
import cv2
import numpy as np
target_window = pygetwindow.getActiveWindow()
monitor = {
        "top": target_window.top,
        "left": target_window.left,
        "width": target_window.width,
        "height": target_window.height,
    }
sct =mss.mss()
img = sct.grab(monitor)
img = np.array(img)
cv2.imshow('test',img)
cv2.waitKey()