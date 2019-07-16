'''
This thread determines whether or not the GUI's RC Tab is selected, and then runs the remote_control_input thread
'''

import MechOS

import pygame
import socket
import struct
import numpy as np
import time
from PyQt5.QtCore import QThread
from MechOS.message_passing.Nodes.node_base import node_base
from remote_control_input import Remote_Control_Node

class RC_Thread(QThread):

    def __init__(self):
        QThread.__init__(self)

        self.threadrunning = False

        rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_address = ('192.168.1.14', 6312)

        IP={'RC':
                {
                'address': ip_address,
                'sockets': (rc_socket, thrust_socket),
                'type': 'UDP'
                }
            }
        MEM={'RC':b'cleaners'}

        self.rc_input_thread = Remote_Control_Node(IP, MEM)
        self.rc_input_thread.rc_thread_running = False
        self.rc_input_thread.start()

    def __del__(self):
        self.wait()

    def run(self):

        while self.threadrunning == False:
            self.rc_input_thread.rc_thread_running = False

        while self.threadrunning == True:
            self.rc_input_thread.rc_thread_running = True
