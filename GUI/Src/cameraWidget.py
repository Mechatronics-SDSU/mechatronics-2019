'''
Copyright 2019, Ramiz Hanan, All rights reserved

Authors:
        Ramiz Hanan <ramizhanan@gmail.com>
        
Last Modified 07/21/2019

Description: Video Recording Utility made with PyQt with option to choose save folder and video name. 
'''
import cv2
import numpy as np
import socket
import sys
import io
import csv
import time
import tkinter
import os

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from MechOS import mechos
from tkinter import filedialog
from datetime import datetime

class record_video_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the Video Recording GUI

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self._file_picker()

    def _file_picker(self):
        '''
        Set up the layout grid for displaying the video recorder.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.vid_format = '.avi'

        orientation_txt = QLabel("<font color='black'>CAM FEED</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        self.orientation_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.flocation_txt = QLabel()
        self.flocation_txt.setText("<font color='black'>File Location</font>")
        self.flocation_box = QLineEdit()
        self.flocation_box.setText("")

        self.fname_txt = QLabel()
        self.fname_txt.setText("<font color='black'>File Name</font>")
        self.fname_box = QLineEdit()

        self.status_txt = QLabel()
        self.status_txt.setText(f"<font color='black'>Choose location and name. Saving as {self.vid_format} </font>")
        

        self.select_location_button = QPushButton("Select File Location")
        self.select_location_button.setStyleSheet("background-color:#999900; color:#E8FFE8")

        self.start_recording_button = QPushButton("Start Recording")
        self.start_recording_button.setStyleSheet("background-color:#2A7E43; color:#E8FFE8")
        self.select_location_button.clicked.connect(self.select_file_location) #connect here
        self.start_recording_button.clicked.connect(self.start_recording)


        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.flocation_txt, 0, 0)
        self.orientation_layout.addWidget(self.flocation_box, 0, 1)
        self.orientation_layout.addWidget(self.fname_txt, 1, 0)
        self.orientation_layout.addWidget(self.fname_box, 1, 1)
        self.orientation_layout.addWidget(self.select_location_button, 2, 0)
        self.orientation_layout.addWidget(self.start_recording_button, 2, 1)
        self.orientation_layout.addWidget(self.status_txt, 3, 0)
        self.linking_layout.addLayout(self.orientation_layout, 1)
        

    def select_file_location(self):
        '''
        Selects file to where video will be saved.

        Parameter:
            N/A
        Returns:
            N/A
        '''
        
        root = tkinter.Tk()
        root.withdraw() #use to hide tkinter window


        currdir = os.getcwd()
        tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
        if len(tempdir) > 0:
            self.flocation_box.setText(tempdir)
        return tempdir


    def start_recording(self):
        '''
        starts video recording

        Parameters:
            N/A
        Returns:
            N/A
        '''
        camera = cv2.VideoCapture(1)

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        # Define the codec and create VideoWriter object to save the video
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        #fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        TimeStamp = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
        print("Video captured:" + TimeStamp)
        #video_writer = cv2.VideoWriter('output.avi', fourcc, 30.0, (800, 600))
        
        fileName = TimeStamp if (self.fname_box.text() == '') else f"{self.fname_box.text()}-{TimeStamp}" #if no name given, use time as filename
        video_writer = cv2.VideoWriter((self.flocation_box.text() + '/' + fileName + self.vid_format), fourcc, 20.0, (800, 600))

        frame_rate = 30
        prev = 0

        while True:
            time_elapsed = time.time() - prev
            (grabbed, frame) = camera.read()  # grab the current frame
            if time_elapsed > 1./frame_rate:
                    prev = time.time()
                
                    cv2.imshow("Frame", frame)  # show the frame to our screen

                    key = cv2.waitKey(33) & 0xFF  

                    video_writer.write(frame)  # Write the video to the file system """ """
                    if key==27:
                        break
        # cleanup the camera and close any open windows
        camera.release()
        video_writer.release()
        cv2.destroyAllWindows()
    

if __name__ == "__main__":
    import sys
    app = QApplication([])
    set_pos_gui = record_video_GUI()
    set_pos_gui.show()
    sys.exit(app.exec_())
