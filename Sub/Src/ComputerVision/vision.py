'''
Copyright 2019, Alexa Becerra, All rights reserved

Authors:Alexa Becerra <alexa.becerra99@gmail.com>
        Mohammad Shafi <ma.shafi99@gmail.com>
        Ramiz Hanan
        Christian Gould <christian.d.gould@gmail.com>
        David Pierce Walker-Howell <piercedhowell@gmail.com>
Last Modified 07/13/2019

Description: Vision (Cam Node) utilizes the neural network and Yolo for object
detection of captured images, that are then sent over a socket to be captured by Recv Node.
'''

import numpy as np
import cv2
import math
import random
import socket
import sys
import os
import struct
import math
import io
import time
from ctypes import *
from libs.darknet import *
from MechOS.message_passing.Nodes.node_base import node_base
from MechOS import mechos
from libs.pose_calculation import Distance_Calculator

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

class Vision(node_base):
    '''
    Vision captures from the webcam, runs the neural network/cv algorithms,  and streams the processed images.
    '''

    def __init__(self, MEM, IP):
        '''
        Initializes values for encoded image streaming, begins webcam capture and
        loads in the neural network.

        Parameters:
            MEM: Dictionary containing Node name and the desired local memory location.
            IP: Dictionary containing Node name and desired streaming settings: The IP address, send
            and recieve sockets, and the streaming protocal.
        '''

        # IP and MEM RAM locations
        node_base.__init__(self, MEM, IP)

        # Instantiations
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        self.neural_network_node = mechos.Node("NEURAL_NETWORK", configs["ip"])
        self.neural_net_publisher = self.neural_network_node.create_publisher("NN", configs["pub_port"])
        self.neural_net_timer = float(self.param_serv.get_param("Timing/neural_network"))

        #--MESSAGING INFO--#
        self.MAX_UDP_PACKET_SIZE = 1500

        # The end byte of the image sent over udp
        self.END_BYTE = bytes.fromhex('c0c0')*2

        # the Max Packet Size the Port will accept
        self.MAX_PACKET_SIZE = 1500

        #--CAMERA INSTANCE--#
        front_camera_index = int(self.param_serv.get_param("Vision/front_camera_index"))
        self.capture = cv2.VideoCapture(front_camera_index)

        # Maximum image size the Tegra allows without timeout
        self.capture.set(3, 450)
        self.capture.set(4, 450)

        # Neural Network Loaded from instance in darknet module
        darknet_path = self.param_serv.get_param("Vision/yolo/darknet_path")
        config_file = self.param_serv.get_param("Vision/yolo/config_file")
        weights_file = self.param_serv.get_param("Vision/yolo/weights_file")
        metadata_file = self.param_serv.get_param("Vision/yolo/metadata_file")
        config_file_path = (os.path.join(darknet_path, config_file)).encode()
        weights_file_path = (os.path.join(darknet_path, weights_file)).encode()
        metadata_file_path = (os.path.join(darknet_path, metadata_file)).encode()
        print(config_file_path, weights_file_path)
        self.net  = load_net(config_file_path,
                       weights_file_path,
                       0)

        self.meta = load_meta(metadata_file_path)

        self.distance_calculator = Distance_Calculator()

    def run(self):
        '''
        The run loop reads image data from the webcam, processes it through Yolo, and
        then encodes it into a byte stream and encapsulation frame to be sent over the socket.
        '''
        start_time = time.time()
        while(True):
            # Capture frame-by-frame
            ret, byte_frame = self.capture.read()

            # Operations on the frame
            '''
            Yolo: Operations on Frame For Yolo
            '''
            if ret:
                r = detect(self.net, self.meta, byte_frame)
                #Savind detetion to class attribute
                self.yolo_detections = r

                #Draw detections in photo
                for i in r:
                    x, y, w, h = i[2][0], i[2][1], i[2][2], i[2][3]

                    #Perform solve pnp calculations
                    self.distance_calculator.set_coordinates(r, i, x, y, w, h)
                    rotation, translation, distance = self.distance_calculator.calculate_distance()
                    #print(distance)
                    xmin, ymin, xmax, ymax = convertBack(float(x), float(y), float(w), float(h))
                    pt1 = (xmin, ymin)
                    pt2 = (xmax, ymax)
                    cv2.rectangle(byte_frame, pt1, pt2, (0, 255, 0), 2)
                    cv2.putText(byte_frame, i[0].decode() + " [" + str(round(i[1] * 100, 2)) + "]", (pt1[0], pt1[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 255, 0], 4)
                    cv2.putText(byte_frame, "[" + str(round(distance, 2)) + "ft]", (pt2[0], pt1[1] + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, [0,127, 127], 4)
                    label = i[0].decode("utf-8")
                    detection_data = struct.pack('sfffffffffff',
                                                 label.encode("utf-8"),
                                                 i[1],
                                                 i[2][0],
                                                 i[2][1],
                                                 i[2][2],
                                                 i[2][3],
                                                 rotation[0],
                                                 rotation[1],
                                                 rotation[2],
                                                 translation[0],
                                                 translation[1],
                                                 translation[2])

                    if ((time.time() - start_time) >= self.neural_net_timer):
                        self.neural_net_publisher.publish(detection_data) #Send the detection data
                        start_time = time.time()

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
    CAM_IP_ADDRESS  = ('192.168.1.2', 6969)

    IP ={'CAMERA':
            {
            'address': CAM_IP_ADDRESS,
            'sockets': (CAMERA_SOCK, RECV_SOCK),
            'type': 'UDP'
            }
        }
    MEM={'CAMERA':b''}

    # Initialize Node Thread
    cam_node = Vision(MEM, IP)
    cam_node.start()
