import numpy
import cv2
import time

MAX_BOUNDING_RECT_AREA_DIFFERENCE = 1.25
AREA_THRESHOLD = 500

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

    # If we, for some strange reason, got a single object instead of a list, put that object in a list
    if type(contourList) is not list:
        contourList = [contourList]

    compareFunction = lambda y, x: int(cv2.contourArea(x) - cv2.contourArea(y))
    contourList = sorted(contourList, cmp = compareFunction)

    return contourList

def vision():
    camera = cv2.VideoCapture(0)

    # If there was a problem opening the camera, exit
    if camera.isOpened() is False:
        raise SystemExit("WTF! cv2.VideoCapture returned None!")

    _, imgInBGR = camera.read()

    picWidth = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    picHeight = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

    picFPS = camera.get(cv2.CAP_PROP_FPS)
    print "fps before set: %d" % (picFPS)
    camera.set(cv2.CAP_PROP_FPS, 15)
    picFPS = camera.get(cv2.CAP_PROP_FPS)

    print "width: %d, height: %d\nfps: %d" % (picWidth, picHeight, picFPS)

    cv2.imshow("Tyson", imgInBGR)
    while cv2.waitKey() is not ord("\n"):
        pass

    # If there was a problem reading the image, exit
    if imgInBGR is None:
        raise SystemExit("WTF! camera.read returned None!")

    lowerLimitInHSV = numpy.array([70, 40, 0], numpy.uint8)
    upperLimitInHSV = numpy.array([160, 190, 255], numpy.uint8)
    imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
    imgMask = cv2.inRange(imgInHSV, lowerLimitInHSV, upperLimitInHSV)

    if cv2.__version__.startswith("3."):
        currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    elif cv2.__version__.startswith("2."):
        currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    else:
        raise SystemExit("WTF! What version of openCV are you using?")


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
        tempImage = numpy.copy(imgInBGR)
        cv2.drawContours(tempImage, [currentContour], 0, (255,255,255), 3)
        cv2.imshow("tyson", tempImage)
        cv2.waitKey()


def main():
    vision()

if __name__ == "__main__":
    main()
