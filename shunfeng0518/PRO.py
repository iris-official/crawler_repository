# -*- coding: cp936 -*-

import numpy as np
import cv2

def imgPRO(slide_path, total_path):
    try:
        font = cv2.FONT_HERSHEY_SIMPLEX
        img = cv2.imread(slide_path)
        temp = img.copy()
        gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        edged = cv2.Canny(gray, 30, 700)
        thresh, contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        img1 = cv2.drawContours(img, contours, -1, (255, 255, 255), -1)
        cv2.imwrite(total_path, img1)
    except Exception as ex:
        print('imgPRO!!!', ex)