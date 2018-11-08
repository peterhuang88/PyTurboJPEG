#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 18:47:10 2018

@author: peter
"""
from turbojpeg import TurboJPEG
import numpy as np
import time
import os
import cv2

IMG_DIR = '/home/peter/Programming/all/train'

def main():
    #time1 = test_opencv()
    #time2 = test_jpegturbo()
    time3 = test_plt()
    #print("Time for opencv: " + str(time1))
    #print("Time for jpegturbo: " + str(time2))
    print("Time for plt: " + str(time3))
    

# 174.56 seconds
# 24.26 seconds, 22.64, 20.69, 17.31, 17.11
def test_jpegturbo():
    # create new TurboJPEG object to load images
    tj = TurboJPEG()
    
    # get list of images and list length
    img_list = os.listdir(IMG_DIR)
   
    start = time.time()
    count = 0
    for imagename in img_list:
        if count % 100 == 0:
            print("Finished image #: " + str(count))
                  
        full_path = IMG_DIR + "/" + imagename
        in_file = open(full_path, 'rb')
        img_array = tj.decode(in_file.read())
        in_file.close()
        count = count + 1
        
    stop = time.time()
    
    return (stop - start)

# 118.89 seconds
# 55.22, 57.61, 48.93, 49.03, 49.19
def test_opencv():
    img_list = os.listdir(IMG_DIR)

    start = time.time()
    count = 0
    for imagename in img_list:
        if count % 100 == 0:
            print("Finished image #: " + str(count))
                  
        full_path = IMG_DIR + "/" + imagename

        img_array = cv2.imread(full_path)
        count = count + 1


    stop = time.time()

    return (stop - start)

# 55.74, 52.78, 53.72, 52.79, 51.66
def test_plt():
    img_list = os.listdir(IMG_DIR)

    start = time.time()
    count = 0
    for imagename in img_list:
        if count % 100 == 0:
            print("Finished image #: " + str(count))
                  
        full_path = IMG_DIR + "/" + imagename

        img_array = plt.imread(full_path)
        count = count + 1


    stop = time.time()

    return (stop - start)
    
if __name__ == '__main__':
    main()
