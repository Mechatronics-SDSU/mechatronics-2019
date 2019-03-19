'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/18/2019
Description: This module is the position estimator using a kalman filter for the
            sub.
'''
import os
import sys

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

import navigation_data_pb2
import threading
from MechOS import mechos
import numpy as np
import time

class Position_Estimator(threading.Thread):
    '''
    This class is meant to be ran as a thread to estimate the position of the
    sub using a Kalman Filter for more accurate estimations.
    '''

    def __init__(self):
        '''
        Initialize the parameters for the position estimator including Kalman
        parameters.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        threading.Thread.__init__(self)

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Node to connect position estimator to mechos network
        self.pos_estimator_node = mechos.Node("POS_EST", configs["ip"])
        self.pos_estimator_node.create_subscriber("NAV", self.unpack_nav_data_callback, configs["sub_port"])

        #Proto buffer containing all of the navigation data
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()

        #Measured Position (column) vector as numpy array.
        #Contains roll, pitch, yaw, depth, x_translation, y_translation
        self.measured_position = np.zeros((6, 1))

        #Belief of actual position state.
        #Contains roll, pitich, yaw, depth, x_position, y_position
        self.belief_position = [0, 0, 0, 0, 0, 0]

        self.threading_lock = threading.Lock()
        self.daemon = True
        self.run_thread = True

    def unpack_nav_data_callback(self, nav_data_proto):
        '''
        Unpack the received navigation data from the mechos subscriber.

        Parameters:
            nav_data_proto: A NAV_DATA type protocol buffer message needed to
                    be unpacked

        Returns:
            N/A
        '''
        self.nav_data_proto.ParseFromString(nav_data_proto)
        self.measured_position[0, 0] = self.nav_data_proto.roll
        self.measured_position[1, 0] = self.nav_data_proto.pitch
        self.measured_position[2, 0] = self.nav_data_proto.yaw
        self.measured_position[3, 0] = self.nav_data_proto.depth
        #print(self.measured_position)

        #TODO: Add Kalman Filter
        with self.threading_lock:
            self.belief_position = list(np.reshape(self.measured_position, 6))

    def run(self):
        '''
        The main loop to run the position estimation thread.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while(self.run_thread):

            #Recieve navigation sensor data if available
            self.pos_estimator_node.spinOnce()
            time.sleep(0.1)

if __name__ == "__main__":
    position_estimator = Position_Estimator()
    position_estimator.run()
