import numpy
import cv2
import time

MAX_BOUNDING_RECT_AREA_DIFFERENCE = 1.15
AREA_THRESHOLD = 400

def shapeFiltering(contourList):
    """
    This function receives a list of contours and filters
    out the contours that aren't approximatly square
    """

    outputList = []
    
    if type(contourList) is not list:
        contourList = [contourList]

    for currentContour in contourList:
        _, _, w, h = cv2.boundingRect(currentContour)
        boundingRectArea = w*h 
        currentContourArea = cv2.contourArea(currentContour)
        if boundingRectArea / currentContourArea < MAX_BOUNDING_RECT_AREA_DIFFERENCE:
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

def sortContours(contourList):
    """
    this function sorts the list of retro-reflectors from big to small
    """

    if type(contourList) is not list:
        contourList = [contourList]

    contourList = sorted(contourList, cmp = lambda y, x: int(cv2.contourArea(x) - cv2.contourArea(y)))

    return contourList

def vision():
    imgInBGR = cv2.imread(r'test1.jpg')

    # If there was a problem reading the image, exit
    if imgInBGR is None:
        raise SystemExit("WTF! cv2.imread returned None!")

    lowerLimitInHSV = numpy.array([70, 50, 0], numpy.uint8)
    upperLimitInHSV = numpy.array([160, 255, 255], numpy.uint8)
    imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
    imgMask = cv2.inRange(imgInHSV, lowerLimitInHSV, upperLimitInHSV)

    currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    print "Number of contours BEFORE all filtering is " + str(len(currentContours))
    
    # Filtering the current contours by area
    currentContours = areaFiltering(currentContours)

    print "Number of contours after area filtering is " + str(len(currentContours))

    # Filtering the current contours by shape
    currentContours = shapeFiltering(currentContours)

    print "Number of contours AFTER all filtering is " + str(len(currentContours))

    # Sort the contours from left to right
    currentContours = sortContours(currentContours)

    for currentContour in currentContours:
        # drawing the contour
        #tempImage = numpy.zeros((480 ,640 ,3), numpy.uint8)
        tempImage = cv2.imread(r'test1.jpg')
        cv2.drawContours(tempImage, [currentContour], 0, (255,255,255), 3)
        cv2.imshow("tyson", tempImage)
        cv2.waitKey()


def main():
    vision()

if __name__ == "__main__":
    main()
