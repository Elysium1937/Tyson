import time
import numpy
import cv2
import socket

MAX_BOUNDING_RECT_AREA_DIFFERENCE = 1.25
AREA_THRESHOLD = 500
HSV_LOW_LIMIT = numpy.array([70, 40, 0], numpy.uint8)
HSV_HIGH_LIMIT = numpy.array([160, 190, 255], numpy.uint8)
IMG_WIDTH = 640
IMG_HEIGHT = 480
MID_SECTION_LEFT_EDGE = 7*IMG_WIDTH/20
MID_SECTION_RIGHT_EDGE = 13*IMG_WIDTH/20
SLEEP_CYCLE_IN_SECONDS = 0.2

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

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)

    picWidth = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    picHeight = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

    _, imgInBGR = camera.read()

    print "width: %d, height: %d" % (picWidth, picHeight)

    # If there was a problem reading the image, exit
    if imgInBGR is None:
        raise SystemExit("WTF! camera.read returned None!")

    imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
    imgMask = cv2.inRange(imgInHSV, HSV_LOW_LIMIT, HSV_HIGH_LIMIT)


    # Drawing the lines that divide the 3 sections
    imgInBGR = cv2.line(imgInBGR, (MID_SECTION_LEFT_EDGE, 0), (MID_SECTION_LEFT_EDGE, IMG_HEIGHT), (100, 0, 120), 2)
    imgInBGR = cv2.line(imgInBGR, (MID_SECTION_RIGHT_EDGE, 0), (MID_SECTION_RIGHT_EDGE, IMG_HEIGHT), (100, 0, 120), 2)

    cv2.imshow("Tyson", imgInBGR)
    cv2.waitKey()

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

    currentContours = sortBySize(currentContours)

    if len(currentContours) == 0:
        print "WHERE ARE THE CONTOURS ORI!!!!!!!!!!!"
        return

    roborioSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    finalContour = currentContours[0]

    # Calculating the center of the contour
    currentMoments = cv2.moments(finalContour)
    centerX = int(currentMoments["m10"] / currentMoments["m00"])

    if centerX < MID_SECTION_LEFT_EDGE:
        # Contour is on the left
        print "Turn left if you want to live"
        try:
            roborioSocket.sendto("0", ("roboRIO-1937-FRC", 61937))
        except:
            print "WTF! Couldn't send to the roborio"
    elif centerX < MID_SECTION_RIGHT_EDGE:
        # Contour is in the center
        print "Move straight if you're not gay"
        try:
            roborioSocket.sendto("1", ("roboRIO-1937-FRC", 61937))
        except:
            print "WTF! Couldn't send to the roborio"
    else:
        # Contour is on the right
        print "Turn right if you like big butts and you caAnnot lie!!!!!!!!"
        try:
            roborioSocket.sendto("2", ("roboRIO-1937-FRC", 61937))
        except:
            print "WTF! Couldn't send to the roborio"

    # drawing the contour
    tempImage = numpy.copy(imgInBGR)
    cv2.drawContours(tempImage, [finalContour], 0, (0, 255, 0), 3)
    cv2.imshow("Tyson", tempImage)
    cv2.waitKey()


def main():
    while True:
        vision()
        time.sleep(SLEEP_CYCLE_IN_SECONDS)

if __name__ == "__main__":
    main()
