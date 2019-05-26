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

                #FIXME: Establish mechOS subscriber to listen for photos being passed

        def __del__(self):

                self.wait()

        def run(self):

                while self.threadrunning == False:

                        print("thread stopped")

                        self.sleep(1)

                while self.threadrunning == True:

                        print("thread running")

                        self.sleep(1)

                        #FIXME: Use subscriber to capture pictures at the same FPS as the sub is moving

                        #FIXME: Save Pictures to text file




