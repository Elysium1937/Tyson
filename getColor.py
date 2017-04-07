import cv2
import numpy

global imgInHSV

IMG_WIDTH = 320
IMG_HEIGHT = 240

def onMouse(event, x, y, flags, param):
    print imgInHSV[y,x]

camera = cv2.VideoCapture(1)

# If there was a problem opening the camera, exit    
if camera.isOpened() is False:
    raise SystemExit("WTF! cv2.VideoCapture returned None!")

# Checks in which cv version we use and adjusts accordingly
if cv2.__version__.startswith("3."):
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
elif cv2.__version__.startswith("2."):
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
else:
    raise SystemExit("WTF! What version of openCV are you using?")

_, imgInBGR = camera.read()

imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
cv2.namedWindow("image")
cv2.setMouseCallback("image", onMouse)
cv2.imshow("image", imgInBGR)
cv2.waitKey()
