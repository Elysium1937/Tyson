import numpy
import cv2
import time

max_bounding_rect_edge_ratio = 1.2

def brightnessFiltering(img):
    """
    this function filters out the darker pixels
    """

    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    lowerLimit = numpy.array([20,0,50])
    upperLimit = numpy.array([110,255,255])
    mask = cv2.inRange(hsv, lowerLimit, upperLimit)

    return mask

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
        #currentBoundingRect = cv2.boundingRect(currentContour)
        #w = currentBoundingRect[0][0] - currentBoundingRect[0][1]
        #h = currentBoundingRect[0][0] - currentBoundingRect[1][0]
        minEdge = min(h, w)
        maxEdge = max(h, w)

        if maxEdge / minEdge < max_bounding_rect_edge_ratio:
            outputList.append(currentContour)

    return outputList

def sortContours(contour_list):
    """
    this function sorts the list of retroreflectors from left to right
    """

    if type(contour_list) is list and len(contour_list) is not 0:
        sorted_list = sorted(contour_list, key = lambda contour: cv2.boundingRect(contour)[0] + 0.5*cv2.boundingRect(contour)[2])
    else:
        sorted_list = []

    return sorted_list

def vision():
    img = cv2.imread(r'test.png', 1)

    if img is not None:
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        lowerLimit = numpy.array([0, 0, 100])
        upperLimit = numpy.array([255, 255, 255])
        imgMask = cv2.inRange(hsv, lowerLimit, upperLimit)

        currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        print "Number of contours = " + str(len(currentContours))
        #YOLO#SWAG#DOPE
        # Filtering the current contours by shape
        contourList = shapeFiltering(currentContours)

        # Sort the contours from left to right
        contourList = sortContours(currentContours)

        if len(contourList) == 1:
            print "Found only one good contour!"

        for currentContour in contourList:
            print currentContour

            # drawing the contour
            blankImage = numpy.zeros((480 ,640 ,3), numpy.uint8)
            cv2.drawContours(blankImage, [currentContour], -1, (255,255,0), 3)
            cv2.imshow("imaguuuuuu", blankImage)
            cv2.waitKey()


def main():
    vision()

if __name__ == "__main__":
    main()
