import time
import numpy
import cv2
from cv2 import *
import os
import socket
import math
import threading

MAX_BOUNDING_RECT_AREA_DIFFERENCE = 1.4
MAXIMUM_HEIGHT_FOR_CONTOUR = 40
MAXIMUM_AREA_DIFFERENCE = 25
IMG_WIDTH = 320
IMG_HEIGHT = 240
MINIMUM_AREA_THRESHOLD = 100 * (IMG_HEIGHT*IMG_WIDTH / 76800)
MAXIMUM_AREA_THRESHOLD = 1500 * (IMG_HEIGHT*IMG_WIDTH / 76800)
SLEEP_CYCLE_IN_SECONDS = 0.00
CROP_HEIGHT = 73
roborioSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    try:
        print "trying to find robo-rio"
        roborio_ip = socket.gethostbyname('roboRIO-1937-FRC')
        break
    except socket.gaierror:
        roborio_ip = False
    finally:
        print "searching in 5 seconds!"
        time.sleep(5)
cap = None
last_v = 215
bad_streak = 0
info = {}
done_count = 0


def calibrate(img):
    old = time.time()
    global done_count
    global info
    info = [None] * 250

    def find_usages(high, low):
        global done_count
        global info
        for value in range(low, high):
            if value % 3 == 0:
                info[value] = calibration_vision(img, value)
        done_count += 1
    cal1 = threading.Thread(target=lambda: find_usages(170, 90))
    cal1.start()
    find_usages(250, 170)
    ratios = []
    while done_count < 2:
        pass
    for i in info:
        if i is not None:
            if i[0] == 2 and len(i) == 2:
                ratios.append((i, i[1] / i[0]))
    ratios.sort(key=lambda x: x[1])
    print time.time() - old, " calibration time"
    try:
        if len(ratios) > 10:
            return info.index(ratios[0][0])
        else:
            return 256
    except IndexError:
        return 256


def shape_filtering(contour_list):
    """
    This function receives a list of contours and filters
    out the contours that aren't approximately square
    """

    output_list = []

    if type(contour_list) is not list:
        contour_list = [contour_list]

    for currentContour in contour_list:
        _, _, w, h = cv2.boundingRect(currentContour)
        bounding_rect_area = w * h
        current_contour_area = cv2.contourArea(currentContour)
        if bounding_rect_area / current_contour_area < MAX_BOUNDING_RECT_AREA_DIFFERENCE and w < h:
            output_list.append(currentContour)

    return output_list


def area_filtering(contour_list):
    """
    filters contours that are not above the threshold
    """

    output_list = []

    if type(contour_list) is not list:
        contour_list = [contour_list]

    for current_contour in contour_list:
        if cv2.contourArea(current_contour) > MINIMUM_AREA_THRESHOLD and cv2.contourArea(current_contour) < MAXIMUM_AREA_THRESHOLD:
            output_list.append(current_contour)

    return output_list


def sort_by_size(contour_list):
    """
    this function sorts the list of retro-reflectors from big to small
    """
    # If we, for some strange reason, got a single object instead of a list, put that object in a list
    if type(contour_list) is not list:
        return [contour_list]
    contour_list = sorted(contour_list, cmp=lambda y, x: int(cv2.contourArea(x) - cv2.contourArea(y)))
    return contour_list


def calibration_vision(img, new_v=215):
    hsv_low_limit = numpy.array([0, 0, new_v], numpy.uint8)
    hsv_high_limit = numpy.array([255, 255, 255], numpy.uint8)
    img_in_bgr = img
    img_in_bgr = cv2.cvtColor(img_in_bgr, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_in_bgr, hsv_low_limit, hsv_high_limit)
    if cv2.__version__.startswith("3."):
        current_contours = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    elif cv2.__version__.startswith("2."):
        current_contours = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    else:
        raise SystemExit("WTF! What version of openCV are you using?")
    basic_size = len(current_contours)
    # Filtering the current contours by area
    current_contours = area_filtering(current_contours)

    # Filtering the current contours by shape
    current_contours = shape_filtering(current_contours)

    # Filters the contours by size (big to small)
    current_contours = sort_by_size(current_contours)
    # Checking if the number of Contours is below 2
    return len(current_contours), basic_size


def vision(img, the_v=215):
    hsv_low_limit = numpy.array([0, 0, the_v], numpy.uint8)
    hsv_high_limit = numpy.array([255, 255, 255], numpy.uint8)
    img_in_bgr = img
    
    # If there was a problem reading the image, exit
    if img_in_bgr is None:
        raise Exception("WTF! No picture given!")

    img_in_hsv = cv2.cvtColor(img_in_bgr, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_in_hsv, hsv_low_limit, hsv_high_limit)

    # finding the contours before filtering them
    if cv2.__version__.startswith("3."):
        current_contours = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    elif cv2.__version__.startswith("2."):
        current_contours = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    else:
        raise Exception("WTF! What version of openCV are you using?")

    # Prints the number of contours before all filtering
    print "Number of contours before all filtering is " + str(len(current_contours))

    # Filtering the current contours by area
    current_contours = area_filtering(current_contours)
    print "Number of contours after area filtering is " + str(len(current_contours))

    # Filtering the current contours by shape
    current_contours = shape_filtering(current_contours)
    print "Number of contours after shape filtering is " + str(len(current_contours))

    # Filters the contours by size (big to small)
    current_contours = sort_by_size(current_contours)

    # Checking if the number of Contours is below 2
    if len(current_contours) < 2:
        value_to_send = 19370
        if roborio_ip:
            roborioSocket.sendto(bytes(str(int(value_to_send))), (roborio_ip, 61937))
        return False

    first_contour = current_contours[0]
    second_contour = current_contours[1]

    # Calculating the center's X of the first contour
    current_moments = cv2.moments(first_contour)
    first_x = int(current_moments["m10"] / current_moments["m00"])

    # Calculating the center's X of the second contour
    current_moments = cv2.moments(second_contour)
    second_x = int(current_moments["m10"] / current_moments["m00"])

    # Calculating the center of the contours
    center_x = (first_x + second_x) / 2

    current_value = (center_x * 6.25)
    current_value = math.floor(current_value)
    temp_image = numpy.copy(img_in_bgr)
    cv2.drawContours(temp_image, [first_contour], 0, (0, 255, 0), 3)
    cv2.drawContours(temp_image, [second_contour], 0, (0, 255, 0), 3)
    cv2.imshow("good", temp_image)
    cv2.waitKey(1)
    if roborio_ip:
        roborioSocket.sendto(bytes(str(current_value)), (roborio_ip, 61937))
        print("----------------We've sent " + str(current_value))
    return str(current_value)


def do_frame(img):
    global last_v
    global bad_streak
    if calibration_vision(img, last_v)[0] != 2:
        if bad_streak >= 3:
            print "uncalibrated"
            v = calibrate(img)
            last_v = v
        else:
            bad_streak += 1
            print "frame unused"
            return False
    else:
        bad_streak = 0
        v = last_v
        print "calibrated"
    if v != 256:
        print vision(img), "used: ", v
    else:
        print "no optimal v"
        if roborio_ip:
            roborioSocket.sendto(bytes(str(0)), (roborio_ip, 61937))


def main(camera):
    old = time.time()
    for i in range(30):
        got, new_img = camera.read()
        new_img = cv2.adaptiveThreshold(new_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        if got:
            do_frame(new_img)
            os.system("cls")
    print "30 frames in ", time.time()-old


if __name__ == "__main__":
    robot_cam = cv2.VideoCapture(0)
    # If there was a problem opening the camera, exit
    if robot_cam.isOpened() is False:
        raise Exception("WTF! cv2.VideoCapture returned None!")

    # Checks in which cv version we use and adjusts accordingly
    if cv2.__version__.startswith("3."):
        robot_cam.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        robot_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
    elif cv2.__version__.startswith("2."):
        robot_cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        robot_cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
    else:
        raise Exception("WTF! What version of openCV are you using?")
    while True:
        main(robot_cam)

""" code fixes """
# dns lookup every packet replaced with one dns query
