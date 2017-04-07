import numpy
import cv2
import socket
import sys
import math
import os

MAX_BOUNDING_RECT_AREA_DIFFERENCE = 2
MAXIMUM_HEIGHT_FOR_CONTOUR = 40
MAXIMUM_AREA_DIFFERENCE = 25
AREA_THRESHOLD = 0
HSV_LOW_LIMIT = numpy.array([45, 0, 180], numpy.uint8)
HSV_HIGH_LIMIT = numpy.array([100, 255, 255], numpy.uint8)
IMG_WIDTH = 320
IMG_HEIGHT = 240
SLEEP_CYCLE_IN_SECONDS = 0.05
ERROR_NOT_ENOUGH_CONTOURS = 19370
roborioSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

os.system("v4l2-ctl -d /dev/video0 -c exposure_auto=1")

def shapeFiltering(contourList):
    """
    This function receives a list of contours and filters
    out the contours that aren't approximately square
    """

    outputList = []

    if type(contourList) is not list:
        contourList = [contourList]

    for currentContour in contourList:
        _, _, w, h = cv2.boundingRect(currentContour)
        boundingRectArea = w * h
        currentContourArea = cv2.contourArea(currentContour)
        if boundingRectArea / currentContourArea < MAX_BOUNDING_RECT_AREA_DIFFERENCE and w < h:
            outputList.append(currentContour)

    return outputList

def areaFiltering(contourList):
    """
    filters contours that are not above the threshold
    """

    outputList = []

    if type(contourList) is not list:
        contourList = [contourList]

    for currentContour in contourList:
        if cv2.contourArea(currentContour) > AREA_THRESHOLD:
            outputList.append(currentContour)

    return outputList

def sortBySize(contourList):
    """
    this function sorts the list of retro-reflectors from big to small
    """

    # If we, for some strange reason, got a single object instead of a list, put that object in a list
    if type(contourList) is not list:
        return [contourList]
    compareFunction = lambda y, x: int(cv2.contourArea(x) - cv2.contourArea(y))
    contourList = sorted(contourList, cmp=compareFunction)
    return contourList

def vision():
    camera = cv2.VideoCapture(0)
    
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

    currentLowerColor = HSV_LOW_LIMIT
    currentHigherColor = HSV_HIGH_LIMIT
        
    while True:
        _, imgInBGR = camera.read()
        
        # If there was a problem reading the image, exit
        if imgInBGR is None:
            raise SystemExit("WTF! camera.read returned None!")

        imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
        imgMask = cv2.inRange(imgInHSV, currentLowerColor, currentHigherColor)

        # finding the contours before filtering them
        if cv2.__version__.startswith("3."):
           currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
        elif cv2.__version__.startswith("2."):
           currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        else:
           raise SystemExit("WTF! What version of openCV are you using?")

        if len(currentContours) == 0:
            cv2.imwrite("picture.png", imgInBGR)
        
        # Prints the number of contours before all filtering
        print "Number of contours before all filtering is " + str(len(currentContours))

        # Filtering the current contours by area
        currentContours = areaFiltering(currentContours)
        print "Number of contours after area filtering is " + str(len(currentContours))

        # Filtering the current contours by shape
        currentContours = shapeFiltering(currentContours)
        print "Number of contours after shape filtering is " + str(len(currentContours))

        # Filters the contours by size (big to small)
        currentContours = sortBySize(currentContours)
        
        if len(currentContours) < 2:
            try:
                roborioSocket.sendto(bytes(str(int(ERROR_NOT_ENOUGH_CONTOURS))), ("roboRIO-1937-FRC", 61937))
            except:
                print "Error: ",sys.exc_info()[0]
            continue

        firstContour = currentContours[0]
        secondContour = currentContours[1]

        # Calculating the center's X of the first contour
        currentMoments = cv2.moments(firstContour)
        firstX = int(currentMoments["m10"] / currentMoments["m00"])

        # Calculating the center's X of the second contour
        currentMoments = cv2.moments(secondContour)
        secondX = int(currentMoments["m10"] / currentMoments["m00"])

        # Calculating the center of the contours
        centerX = (firstX + secondX) / 2

        currentValue = math.floor(centerX * (2000/IMG_WIDTH))

        try:
            roborioSocket.sendto(bytes(str(currentValue)), ("roboRIO-1937-FRC", 61937))
            print("----------------We've sent "+ str(currentValue))   
        except:
            print "Error: ",sys.exc_info()[0]

def main():
    vision()

if __name__ == "__main__":
    main()
