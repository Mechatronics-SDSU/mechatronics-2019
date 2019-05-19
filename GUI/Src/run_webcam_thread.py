import sys
import os

from webcam_thread import Webcam_Thread

class Run_Webcam_Thread():

    def __init__(self):
        print("here")
        self.web_thread = Webcam_Thread()
        self.web_thread.start()
