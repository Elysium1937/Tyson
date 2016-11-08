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
    This function receives a list of contours and filters out the contours that aren't shaped like U's
    """

    outputList = []
    if type(contourList) is not list:
        contourList = [contourList]

    for currentContour in contourList:
        currentBoundingRect = cv2.boundingRect(currentContour)
        w = currentBoundingRect[0][0] - currentBoundingRect[0][1]
        h = currentBoundingRect[0][0] - currentBoundingRect[1][0]
        minEdge = min(h, w)
        maxEdge = max(h, w)
        if minEdge * max_bounding_rect_edge_ratio > maxEdge:
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

    img = cv2.imread(r'example.jpg', 1)

    if img is not None:
        # imgMask = brightnessFiltering(img)

        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        lowerLimit = numpy.array([0, 0, 0])
        upperLimit = numpy.array([255, 255, 255])
        imgMask = cv2.inRange(hsv, lowerLimit, upperLimit)

        currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

        print "Number of contours = " + str(len(currentContours))

        # Filtering the current contours by shape
        contourList = shapeFiltering(currentContours)

        # Sort the contours from left to right
        contourList = sortContours(currentContours)

        if len(contourList) == 1:
            print "Found only one good contour!"
            
        for currentContour in contourList:
            print currentContour

def main():
    while True:
        vision()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
