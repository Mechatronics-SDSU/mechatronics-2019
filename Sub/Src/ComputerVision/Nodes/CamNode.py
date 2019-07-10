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
from yolo_wrapper import *

# Port Information
HOST    = '192.168.1.20'
ADDRESS = 6666 # Doom Eternal
OURSOCKET=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Data Size per Packet
MAX_UDP_PACKET_SIZE = 1500

# Encapsulation information
ENCAPSULATION_0xC0 = bytes.fromhex('c0c0')

# videoCapture from Webcam
cap = cv2.VideoCapture(1)
cap.set(3, 450)
cap.set(4, 450)

# load yolo here
net = load_net(b"cfg/yolov3-tiny.cfg",
               b"weights/yolov3-tiny_200.weights",
               0)
meta = load_meta(b"cfg/coco.data")
fps = cap.get(cv2.CAP_PROP_FPS)
print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

while(True):
    # Capture frame-by-frame
    ret, byte_frame = cap.read()


#    input('press enter to continue...')
    # Check Video Size
#    print(frame.shape[:2])

    # print('NO imencode',sys.getsizeof(frame))

    # Operations on the frame
    '''
    Yolo: Operations on Frame For Yolo
    '''
    if ret:
        r = detect(net, meta, byte_frame)

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

        number_of_packets = math.ceil(image_size/MAX_UDP_PACKET_SIZE)
        packet_size = math.ceil(image_size/number_of_packets)

        # Uncomment for Manual Control of Send Speed:

#        info_print='''
#        IMAGE  SIZE:       {}
#        PACKET SIZE:       {}
#        NUMBER OF PACKETS: {}
#        '''.format(image_size, packet_size, number_of_packets)

#        print(info_print)
#        input('Press Enter to Continue...')

        # Count out the number of packets that need to be sent
        for count_var in range(0, number_of_packets):

            OURSOCKET.sendto(imageBuffer.read(packet_size), (HOST, ADDRESS))

        # EOF packet for encapsulation
        OURSOCKET.sendto( ENCAPSULATION_0xC0*2, (HOST, ADDRESS))

        # Image Corruption decreases as sleep time increases (inversely proportional)
        # this time.sleep is a manual fix balacing speed and the least
        # amount of corruption on jpegs (not optimal)
        time.sleep(0) # check as appropriate

    else:
        time.sleep(0)



# When everything done, release the capture
cap.release()
