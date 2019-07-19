'''
Copyright 2019, Alexa Becerra, All rights reserved

Authors:Alexa Becerra <alexa.becerra99@gmail.com>
        Mohammad Shafi
        Ramiz Hanan

Last Modified 07/13/2019

Description: Recv Node captures an image byte stream and displays it.
'''
import numpy as np
import cv2
import socket
import sys
import io
import csv
import time

from MechOS.message_passing.Nodes.node_base import node_base
from datetime import datetime


class Receive_Video_Stream(node_base):
    '''
    Recv Node captures the image data, resizes the image, and displays it.
    '''
    def __init__(self, MEM, IP):
        '''
        Sets the size of data packets, whether or not the image should be resized
        and if images should be saved.

        Parameters:
            MEM: Dictionary containing Node name and the desired local memory location.
            IP: Dictionary containing Node name and desired streaming settings: The IP address, send
            and recieve sockets, and the streaming protocal.
        '''

        node_base.__init__(self, MEM, IP)

        # Data Size Per Packet
        self.MAX_UDP_PACKET_SIZE = 1500

        # Resize image
        self.resize_image = True
        self.scale_percent = 250

        # Collect Images (Switch to False for speed)
        self.save_image = True

        self.ramBuffer = b''

    def run(self):
        '''
        The loop decapsulates recieved image data and stores it in a buffer to be resized/saved/displayed.
        '''

        while(True):
            # Socket Max receive
            # packet = sock.recv(MAX_UDP_PACKET_SIZE)
            packet = self._recv('CAMERA', local=False)
            #print(packet)

            if packet:
                # Buffer object (concatenated byteString)
                self.ramBuffer += packet

                # Triple CRC bytestring and EOF byte
                if (self.ramBuffer.endswith(b'\xc0\xc0\xc0\xc0')):

                    # Decapsulate Byte String (4 sets of 2 chars)
                    self.ramBuffer = self.ramBuffer[:-4]

                    # Image integrity Data Check (imperfect)
                    if ( self.ramBuffer.startswith(b'\xff\xd8') and self.ramBuffer.endswith(b'\xff\xd9') ):

                        # Capture Bytes
#                        print('Recieved Bytes', ramBuffer)
#                        input('press enter to continue...')

                        img_frame = cv2.imdecode(np.frombuffer(self.ramBuffer, dtype=np.uint8), 1)

                        # Our operations on the frame are here (if any)

                        if self.save_image:
                            TimeStamp = str(datetime.now()).replace(' ', '_').replace(':','#')[:-7]
                            cv2.imwrite("/home/piercedhowell/imgs_07_18_19_frame{}.jpg".format(TimeStamp), img_frame)

                        if self.resize_image:
                            # Frame Size (reversed in np.shape)
                            self.scale_percent = 250 # percent of original size

                            width = int(img_frame.shape[1] * self.scale_percent / 100)
                            height = int(img_frame.shape[0] * self.scale_percent / 100)

                            # Make Sure User didn't Blindly initialize Node
                            if not (width or height):
                                raise ValueError('Please Specify FRAME WIDTH and FRAME HEIGHT')

                            dim = (width, height)
                            # resize image
                            img_frame = cv2.resize(img_frame, dim, interpolation = cv2.INTER_AREA)

                        # Display the resulting frame
                        cv2.imshow('CAPTURE', img_frame)

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                    # Clear Buffer
                    self.ramBuffer = b''

            else:
                time.sleep(0)

if __name__=='__main__':
    # Port Information
    HOST    = '192.168.1.1'
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

    # Initialize Node Thread
    recv_node = Receive_Video_Stream(MEM, IP)
    recv_node.start()
