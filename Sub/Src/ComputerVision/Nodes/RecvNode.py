import numpy as np
import cv2
import socket
import sys
import io
import csv
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Port Information
HOST    = '127.0.0.101'
ADDRESS = 6666 # Doom Eternal
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, ADDRESS))

# Data Size Per Packet
MAX_UDP_PACKET_SIZE = 256

FRAME_WIDTH = None
FRAME_HEGHT = None

# Make Sure User didn't Blindly initialize Node
if not (FRAME_WIDTH or FRAME_HEIGHT):
    raise ValueError('Please Specify FRAME WIDTH and FRAME HEIGHT')


# TimeStamp of Capture (looks complicated but does something like this 2019-4-2-secondsmins etc.
TimeStamp = str(datetime.now()).replace(' ', '_').replace(':','#')[:-7]

# Note: Comment Out VideoStuff for Speed Increase
video_file = cv2.VideoWriter('VideoCapture{}.avi'.format(TimeStamp),cv2.VideoWriter_fourcc('M','J','P','G'), 15, (FRAME_WIDTH,FRAME_HEGHT))
ramBuffer = b''

while(True):

    # Socket Max receive
    packet = sock.recv(MAX_UDP_PACKET_SIZE)

    if packet:
        # Buffer object (concatenated byteString)
        ramBuffer += packet

        # Triple CRC bytestring and EOF byte
        if (ramBuffer.endswith(b'\xc0\xc0\xc0\xc0')):

            # Decapsulate Byte String (4 sets of 2 chars)
            ramBuffer = ramBuffer[:-4]

            # Image integrity Data Check (imperfect)
            if ( ramBuffer.startswith(b'\xff\xd8') and ramBuffer.endswith(b'\xff\xd9') ):

                #Capture Bytes
#                print('Recieved Bytes', ramBuffer)
#                input('press enter to continue...')

                img_frame = cv2.imdecode(np.frombuffer(ramBuffer, dtype=np.uint8), 1)

                # Our operations on the frame come here (if any)
                '''
                imageToVideo: Turn OpenCV images into Video Ouput
                '''
                video_file.write(img_frame)

                # Display the resulting frame
                cv2.imshow('Capture', img_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Clear Buffer
            ramBuffer = b''

    else:
        time.sleep(0)

# When everything done, release the capture
cv2.destroyAllWindows()
