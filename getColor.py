import cv2
import numpy

global imgInHSV

def onMouse(event, x, y, flags, param):
    print imgInHSV[y,x]

imgInBGR = cv2.imread("./test.png", 1)
imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
cv2.namedWindow("image")
cv2.setMouseCallback("image", onMouse)
cv2.imshow("image", imgInBGR)
cv2.waitKey()
