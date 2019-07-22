import cv2
import numpy as np
import socket
import sys
import io
import csv
import time
import tkinter
import os
import receive_video_stream

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from MechOS import mechos
from tkinter import filedialog
from datetime import datetime

class record_video_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the Desired Position GUI

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self._file_picker()
        

        

    def _file_picker(self):
        
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
        # Initialize Node Thread
        timestamp = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
        print(timestamp)
        
        file_name = timestamp if (self.fname_box.text() == '') else f"{self.fname_box.text()}-{timestamp}"
        full_path = self.flocation_box.text() + '/' + file_name + self.vid_format
        recv_node = receive_video_stream.Receive_Video_Stream(MEM, IP, full_path)
        recv_node.start()
        
    

if __name__ == "__main__":
    # Port Information
    HOST    = '127.0.0.101'
    PORT    = 6969

    CAMERA_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    RECV_SOCK   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # IP initialization
    IP_ADDRESS = (HOST, PORT)
    RECV_SOCK.bind((IP_ADDRESS))

    IP ={'CAMERA':
            {
            'address': IP_ADDRESS,
            'sockets': (CAMERA_SOCK, RECV_SOCK),
            'type': 'UDP'
            }
        }
    MEM={'CAMERA':b''}
    app = QApplication([])
    set_pos_gui = record_video_GUI()
    set_pos_gui.show()
    sys.exit(app.exec_())
