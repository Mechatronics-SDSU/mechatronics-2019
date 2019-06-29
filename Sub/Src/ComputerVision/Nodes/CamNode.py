import numpy as np
import cv2
import socket
import sys
import struct
import math
import io
import time

HOST    = '127.0.0.101'
ADDRESS = 5558
MAX_UDP_PACKET_SIZE = 1024

ENCAPSULATION_0xC0 = bytes.fromhex('c0c0')

OURSOCKET=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # print('NO imencode',sys.getsizeof(frame))
    # Capture Bytes
    ret, byte_frame = cv2.imencode( '.jpg', frame )

    # Operations on the frame

    '''
    None: No operations on Frame
    '''

    # Get the Size of the image
    image_size = sys.getsizeof(byte_frame)

    # Max Byte Size
    if image_size:

        imageBuffer = io.BytesIO(byte_frame)

        number_of_packets = math.ceil(image_size/MAX_UDP_PACKET_SIZE)
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

            OURSOCKET.sendto(imageBuffer.read(packet_size), (HOST, ADDRESS))

        # EOF packet for encapsulation
        OURSOCKET.sendto( ENCAPSULATION_0xC0*2, (HOST, ADDRESS))
        #TODO Check this sleep regularly for improvements or deletion
        time.sleep(0.0) # Internal Man Config for packet loss

    else:
        time.sleep(0)



# When everything done, release the capture
cap.release()

