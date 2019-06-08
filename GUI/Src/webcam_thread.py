'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino<Claire Fiorino>
Last Modified 04/27/2019
Description: This PyQt thread is for printing the paths of the jpeg images to a text file to train the YOLO network. 
'''

import sys
import os
import time

from PyQt5.QtCore import QThread

class Webcam_Thread(QThread):

        def __init__(self):

                QThread.__init__(self)

                #"num" is the number of the jpeg image that is saved
                self.num = 0        

        def __del__(self):

                self.wait()

        def print_image_names(self):
                '''
        This opens the "train.txt" file and prints the paths of each jpeg image
        '''

                #FIXME: Will make file in directory "build\darknet\x64\data\
                yfile = open("train.txt", "a")
                
                #Print image paths in text file
                image_name = "data/obj/img"+(str)(self.num)+".jpg"
                yfile.write(image_name)
                yfile.write("\n")

        def run(self):

                while self.threadrunning == False:

                        self.sleep(1)

                while self.threadrunning == True:

                        self.print_image_names()

                        self.num = self.num+1

                        self.sleep(.1) #argument inside sleep function has to align with the rate at which the sub is taking pictures





