import numpy as np
import cv2
import io
import socket
from message_passing.Nodes.node_base_udp import node_base
#from cv2 import cv


class receiver_node(node_base):

    def __init__(self, IP, MEM):

        node_base.__init__(self, MEM, IP)

    def run(self):
        while (True):
            img_bytes = self._recv('Camera', local=False)
            img = cv2.decode(img_bytes, cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imshow('img', img)


if __name__ == '__main__':

    camera_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('127.0.0.101', 5558)
    MEM = {'Sometimes': 'Never'}
    IP ={"Camera":
                 {
                 'address': ip_address,
                 'sockets': (camera_socket, receiver_socket),
                 'type': 'UDP'
                 }
        }

    receive_node = receiver_node(IP, MEM)
    receive_node.start()
