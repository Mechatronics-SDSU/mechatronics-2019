import numpy as np
import cv2
import io
import socket
from message_passing.Nodes.node_base_udp import node_base
import sys

class camera_node(node_base):

    def __init__(self, IP, MEM):

        node_base.__init__(self, MEM, IP)
        self._cap = cv2.VideoCapture(1)

    def run(self):

        while(True):
            ret, frame = self._cap.read()
            frame_size = sys.getsizeof(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            io_buf = io.BytesIO(buffer)
            #print(io_buf.read())
            self._send(frame_size, register = "Size", local = True, foreign = False)
            self._send(io_buf.read(65000), register = "Camera", local = False, foreign = True)

        self._cap.release()
        cv2.destroyAllWindows()

class receiver_node(node_base):

    def __init__(self, IP, MEM):

        node_base.__init__(self, MEM, IP)
        self._buffer = None

    def run(self):
        while (True):

            frame_size = self._recv("Size", local = True)
            print(frame_size)
            img_bytes = self._recv("Camera", local=False)
            pic_size = sys.getsizeof(img_bytes)
            print(sys.getsizeof(img_bytes))
            self._buffer = io.BytesIO(img_bytes)
            img = cv2.imdecode(self._buffer, cv2.IMREAD_COLOR)
            cv2.imshow('img', img)

if __name__ == '__main__':

    camera_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('127.0.0.101', 5558)
    receiver_socket.bind((ip_address))
    MEM = {"Size": 20}
    IP ={"Camera":
                 {
                 'address': ip_address,
                 'sockets': (camera_socket, receiver_socket),
                 'type': 'UDP'
                 }
        }

    cam_node = camera_node(IP, MEM)
    receive_node = receiver_node(IP, MEM)
    cam_node.start()
    receive_node.start()
