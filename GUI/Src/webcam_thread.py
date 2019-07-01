'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino<Claire Fiorino>
Last Modified 04/27/2019
Description: This PyQt thread is for printing the paths of the jpeg images to a text file to train the YOLO network. 
'''

import sys
import os
import datetime
import time
import socket

from PyQt5.QtCore import QThread

class Webcam_Thread(QThread):

        def __init__(self):

                QThread.__init__(self)

                #"imageNumber" is the number of the jpeg image that is saved
                self.packetCount = 0
                self.imageNumber = 1        

        def __del__(self):

                self.wait()

        def print_image_names(self):
                '''
        This opens the "train.txt" file and prints the paths of each jpeg image
        '''

                yfile = open("train.txt", "a")
                
                #Print image paths in text file
                image_name = "data/obj/img"+(str)(self.imageNumber)+".jpg"
                yfile.write(image_name)
                yfile.write("\n")

        def run(self):

                while self.threadrunning == False:

                        self.sleep(0)

                while self.threadrunning == True:

                        HOST = '127.0.0.1'  # The server's hostname or IP address
                        PORT = 65432        # The port used by the server

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.connect((HOST, PORT))
                                s.sendall(b'pic taken')
                                #data = s.recv(1024)

                        while True:
                                time.sleep(1) #TAKE THIS OUT
                                self.packetCount += 1 #For every packet recieved increment packetCount
                                print (self.packetCount)
                                if self.packetCount % 3 == 0: #For every three packets received
                                        self.imageNumber += 1
                                        print("IMAGE NUMBER: " + (str)(self.imageNumber))
                                        self.print_image_names()
                        
                        self.num = self.num+1
                        time.sleep(.1)






