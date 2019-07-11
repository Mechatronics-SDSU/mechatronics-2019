import numpy as np
import cv2
import math
import random
import socket
import sys
import struct
import math
import io
import time
from ctypes import *
from libs.darknet import *
from MechOS.message_passing.Nodes.node_base import node_base

class CamNode(node_base):

    def __init__(self, MEM, IP):

        # IP and MEM RAM locations
        node_base.__init__(self, MEM, IP)

        # Instantiations

        #--MESSAGING INFO--#
        self.MAX_UDP_PACKET_SIZE = 1500

        # The end byte of the image sent over udp
        self.END_BYTE = bytes.fromhex('c0c0')*2

        # the Max Packet Size the Port will accept
        self.MAX_PACKET_SIZE = 1500

        #--CAMERA INSTANCE--#
        self.capture = cv2.VideoCapture(1)

        # Maximum image size the Tegra allows without timeout
        self.capture.set(3, 450)
        self.capture.set(4, 450)

        # Neural Network Loaded from instance in darknet module
        self.net  = load_net(b'./libs/darknet/cfg/yolov3-tiny.cfg',
                       b'./libs/darknet/weights/yolov3-tiny.weights',
                       0)

        self.meta = load_meta(b'./libs/darknet/cfg/coco.data')

        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(self.fps))

    def run(self):
        while(True):
            # Capture frame-by-frame
            ret, byte_frame = self.capture.read()

            # Operations on the frame
            '''
            Yolo: Operations on Frame For Yolo
            '''
            if ret:
                r = detect(self.net, self.meta, byte_frame)

                for i in r:
                    x, y, w, h = i[2][0], i[2][1], i[2][2], i[2][3]
                    xmin, ymin, xmax, ymax = convertBack(float(x), float(y), float(w), float(h))
                    pt1 = (xmin, ymin)
                    pt2 = (xmax, ymax)
                    cv2.rectangle(byte_frame, pt1, pt2, (0, 255, 0), 2)
                    cv2.putText(byte_frame, i[0].decode() + " [" + str(round(i[1] * 100, 2)) + "]", (pt1[0], pt1[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 255, 0], 4)
                # Get the Size of the image
                image_size = sys.getsizeof(byte_frame)

            # Capture Bytes
            ret, byte_frame = cv2.imencode( '.jpg', byte_frame )

            # Sending The Frame
            if ret:
                imageBuffer = io.BytesIO(byte_frame)

                number_of_packets = math.ceil(image_size/self.MAX_UDP_PACKET_SIZE)
                packet_size = math.ceil(image_size/number_of_packets)

                # Uncomment for Manual Control of Send Speed:

                #info_print=
                '''
                IMAGE  SIZE:       {}
                PACKET SIZE:       {}
                NUMBER OF PACKETS: {}
                '''
                #.format(image_size, packet_size, number_of_packets)

                #print(info_print)
                #input('Press Enter to Continue...')

                # Count out the number of packets that need to be sent
                for count_var in range(0, number_of_packets):

                    self._send(imageBuffer.read(packet_size), 'CAMERA', local=False, foreign=True)

                # EOF packet for encapsulation
                self._send(self.END_BYTE, 'CAMERA', local=False, foreign=True)

# Image Corruption decreases as sleep time increases (inversely proportional)
                # this time.sleep is a manual fix balacing speed and the least
                # amount of corruption on jpegs (not optimal)
                #time.sleep(0) # check as appropriate

            else:
                time.sleep(0)

if __name__=='__main__':

    CAMERA_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    RECV_SOCK   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # IP initialization
    IP_ADDRESS  = ('192.168.1.20', 6969)

    IP ={'CAMERA':
            {
            'address': IP_ADDRESS,
            'sockets': (CAMERA_SOCK, RECV_SOCK),
            'type': 'UDP'
            }
        }
    MEM={'CAMERA':b''}

    # Initialize Node Thread
    cam_node = CamNode(MEM, IP)
    cam_node.start()

