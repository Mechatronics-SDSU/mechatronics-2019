import sys
import os
import time

from PyQt5.QtCore import QThread

class Webcam_Thread(QThread):

        def __init__(self):

                QThread.__init__(self)

                self.threadrunning = False
                print("Thread initiated")

                #FIXME: Set up camera/start streaming

        def __del__(self):

                self.wait()

        def run(self):

                #FIXME: Use subscriber to capture pictures at the same FPS as the sub is moving

                while self.threadrunning == False:

                        self.sleep(1)

                while self.threadrunning == True:

                        print("thread running")

                        #FIXME: Print picures, coordinates, and label

                        #FIXME: Save Pictures to text file



