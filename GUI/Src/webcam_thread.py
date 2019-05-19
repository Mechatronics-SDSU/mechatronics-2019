import sys
import os
import time

from PyQt5.QtCore import QThread

from image_capture_widget import Image_Capture

class Webcam_Thread(QThread):

        def __init__(self):

                QThread.__init__(self)
                self.x = 0
                print("Thread initiated")
                #FIXME: Set up camera/start streaming

        def __del__(self):

                self.wait()

        def run(self):

                #FIXME: Use subscriber to capture pictures at the same FPS as the sub is moving

                while Image_Capture.threadrunning == False:
                        print("Thread stopped")
                        time.sleep(1)

                while Image_Capture.threadrunning == True:

                        #FIXME: Print picures, coordinates, and label

                        #Open text file to write values
                        yfile = open("yolo_data.txt", "a")

                        #Save individual values of x and y for upper left coordinate to print later
                        self.point1x = Image_Capture.begin.x()
                        self.point1y = Image_Capture.begin.y()

                        #Print upper left coordinate of rectangle
                        yfile.write("("+self.image_lab.cb.currentText()+") ")
                        yfile.write("COORDINATES #"+(str)(self.i+1)+": ")
                        point = " ("+(str)(self.point1x)+", "+(str)(self.point1y)+")"
                        yfile.write(point)

                        #Update coordinate number
                        self.i = Image_Capture.i+1
                        self.update()

                        time.sleep(1)

                        #FIXME: Save Pictures to text file



