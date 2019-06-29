import numpy as np
import cv2
import socket
import sys
import io
import csv
import matplotlib.pyplot as plt

HOST    = '127.0.0.101'
ADDRESS = 5558

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, ADDRESS))

MAX_UDP_PACKET_SIZE = 1024
#cap = cv2.VideoCapture(0)

ramBuffer = b''

while(True):

    # Socket Max receive
    packet = sock.recv(MAX_UDP_PACKET_SIZE)
    if packet:

        # Buffer object (concatenated byteString)
        ramBuffer += packet

        # Triple CRC bytestring and EOF byte
        if (ramBuffer.endswith(b'\xc0\xc0\xc0\xc0')):

            #Capture Bytes
            print('Recieved Bytes', ramBuffer)

            # Decapsulate Byte String (4 sets of 2 chars)
            ramBuffer = ramBuffer[:-4]

            try:
                img_frame = cv2.imdecode(np.frombuffer(ramBuffer, dtype=np.uint8), 1)
            except:
                break
            #ret, img_frame = cv2.imdecode('.jpg', ramBuffer)

            # Our operations on the frame come here (if any)

            '''
            None: No operations Specified
            '''

            # Display the resulting frame

            cv2.imshow( 'FRAME', img_frame)
            cv2.waitKey(1)

            # Clear Buffer
            ramBuffer = b''

            if cv2.waitKey(1) & 0xFF == ord('q'):
               break
    else:
        time.sleep(0)

# When everything done, release the capture
cv2.destroyAllWindows()
