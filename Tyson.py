import time
import numpy
import cv2
import socket
from timeit import default_timer as timer
import sys
import traceback

MAX_BOUNDING_RECT_AREA_DIFFERENCE = 1.4
AREA_THRESHOLD = 500
HSV_LOW_LIMIT = numpy.array([60, 140, 180], numpy.uint8)
HSV_HIGH_LIMIT = numpy.array([75, 150, 255], numpy.uint8)
IMG_WIDTH = 640
IMG_HEIGHT = 480
MID_SECTION_LEFT_EDGE = 7*IMG_WIDTH/20
MID_SECTION_RIGHT_EDGE = 13*IMG_WIDTH/20
SLEEP_CYCLE_IN_SECONDS = 0.2
roborioSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def HandleSingleContour(singleContour):
     finalContour = singleContour

    # Calculating the center of the contour
     currentMoments = cv2.moments(finalContour)
     centerX = int(currentMoments["m10"] / currentMoments["m00"])
     ValueToSend = -1 #Indicator
     if centerX < MID_SECTION_LEFT_EDGE:
         # Contour is on the left
         print "Turn left"
         ValueToSend = 0  
     elif centerX < MID_SECTION_RIGHT_EDGE:
         # Contour is in the center
         print "Move straight"
         ValueToSend = 1
     else:
         # Contour is on the right
         ValueToSend = 2

     try:
          roborioSocket.sendto(bytes(str(ValueToSend)), ("roboRIO-1937-FRC", 61937))
          print("Sent -------------------------------------------------Sent")  
     except:
          print "Error: ",sys.exc_info()[0]
          traceback.print_exc()
          raise SystemExit("WTF! Couldn't send to the roborio")
         
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

def Statistics(counterLeft,counterStraight,counterRight):
     if counterLeft+counterStraight+counterRight > 9:
          if counterLeft > 6:
               return

def vision():
    #count = 0
    #start = timer()
    camera = cv2.VideoCapture(0)
    counterLeft = 0
    counterStraight = 0
    counterRight = 0

    # If there was a problem opening the camera, exit
    if camera.isOpened() is False:
        raise SystemExit("WTF! cv2.VideoCapture returned None!")

    if cv2.__version__.startswith("3."):
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
    elif cv2.__version__.startswith("2."):
        camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
    else:
        raise SystemExit("WTF! What version of openCV are you using?")

    while True:
         #count=count+1
         #print "iteration " + str(count) + " time was " + str(timer()-start)
         #start = timer()

         _, imgInBGR = camera.read()

         # If there was a problem reading the image, exit
         if imgInBGR is None:
             raise SystemExit("WTF! camera.read returned None!")

         imgInHSV = cv2.cvtColor(imgInBGR, cv2.COLOR_BGR2HSV)
         imgMask = cv2.inRange(imgInHSV, HSV_LOW_LIMIT, HSV_HIGH_LIMIT)


         # Drawing the lines that divide the 3 sections
         imgInBGR = cv2.line(imgInBGR, (MID_SECTION_LEFT_EDGE, 0), (MID_SECTION_LEFT_EDGE, IMG_HEIGHT), (100, 0, 120), 2)
         imgInBGR = cv2.line(imgInBGR, (MID_SECTION_RIGHT_EDGE, 0), (MID_SECTION_RIGHT_EDGE, IMG_HEIGHT), (100, 0, 120), 2)

         if cv2.__version__.startswith("3."):
             currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
         elif cv2.__version__.startswith("2."):
             currentContours = cv2.findContours(imgMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
         else:
             raise SystemExit("WTF! What version of openCV are you using?")

         print "Number of contours before all filtering is " + str(len(currentContours))

         # Filtering the current contours by area
         currentContours = areaFiltering(currentContours)

         print "Number of contours after area filtering is " + str(len(currentContours))

         # Filtering the current contours by shape
         currentContours = shapeFiltering(currentContours)

         print "Number of contours after shape filtering is " + str(len(currentContours))

         currentContours = sortBySize(currentContours)

         # Checking if the number of Contours is below 2 
         if len(currentContours) < 2:
             # If found 1 Contour, goes to a function that deals with 1 Contour
             if len(currentContours) == 1:
                 HandleSingleContour(currentContours[0])
                 print "Found one Contour"
             else:
                 #If found no Contours, does nothing
                 print "Couldn't find contours"
             continue
         if len(currentContours) > 0:
              tempImage = numpy.copy(imgInBGR)
              for contour in currentContours:
                   cv2.drawContours(tempImage, [contour], 0, (0, 255, 0), 3)
              cv2.imwrite("picture.png", tempImage)
              print "WTF! Too many Contours"
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

         if centerX <= MID_SECTION_LEFT_EDGE:
             # Contour is on the left
             print "Turn left"
             #currentValue = (centerX / MID_SECTION_LEFT_EDGE) * -1
             counterLeft += 1
             currentValue = 0 
         elif centerX > MID_SECTION_LEFT_EDGE and centerX < MID_SECTION_RIGHT_EDGE:
             # Contour is in the center
             print "Move straight"
             counterStraight += 1
             currentValue = 1
         elif centerX >= MID_SECTION_RIGHT_EDGE:
             # Contour is on the right
             print "Turn right"
             counterRight += 1
             #currentValue = (centerX - MID_SECTION_RIGHT_EDGE)/(IMG_WIDTH - MID_SECTION_RIGHT_EDGE)
             currentValue = 2
         try:
             roborioSocket.sendto(bytes(str(currentValue)), ("roboRIO-1937-FRC", 61937))
             print("Sent -------------------------------------------------Sent")  
         except:
             print "Error: ",sys.exc_info()[0]
             traceback.print_exc()
             raise SystemExit("WTF! Couldn't send to the roborio")

         # drawing the contour - Currently useless?
         
         tempImage = numpy.copy(imgInBGR)
         cv2.drawContours(tempImage, [finalContour], 0, (0, 255, 0), 3)
         cv2.imshow("Tyson", tempImage)
         cv2.waitKey()
         
         print "Turn lefts " + str(counterLeft)
         print "Turn straighta " + str(counterStraight)
         print "Turn rights " + str(counterRight)
         time.sleep(SLEEP_CYCLE_IN_SECONDS)


def main():
    #roborioSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    vision()

if __name__ == "__main__":
    main()
