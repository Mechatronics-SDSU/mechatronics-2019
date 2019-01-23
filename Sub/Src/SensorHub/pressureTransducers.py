'''
Copyright 2018, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 12/22/2018
Description: This module is the driver of the pressure transducers on the sub
                used for determining depth.
'''
import sys
import os
HELPERS_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPERS_PATH)
PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from MechOS import mechos
from sensorHub import SensorHubBase
import serial
import time
import struct
from protoFactory import packageProtobuf
import Mechatronics_pb2
import numpy as np
from Kalman_Filter import Kalman_Filter
import threading



class Pressure_Depth_Transducers(threading.Thread, SensorHubBase):
    '''
    Receive Pressure and Depth data from each pressure transducer. Filter the data
    and fuse each sensors data for a less noisey reading using a Kalman Filter.
    '''
    def __init__(self, com_ports):
        '''
        Initialize communication with each pressure transducer. And set up MechOS
        node to communicate data over the MechOS network.

        Parameters:
            com_ports: A list of com ports that the pressure transducers are
                        connected to.

        Returns:
            N/A
        '''
        #Initialize base classes
        super(Pressure_Depth_Transducers, self).__init__()

        self.type = "PRESSURE_TRANSDUCERS"

        #ovveride the parent publisher attribute
        #currently only going to transmit depth data
        self.sensorHub_transducers = mechos.Node("SENSORHUB_PRESSURE_TRANSDUCERS")
        self.publisher = self.sensorHub_transducers.create_publisher("DEPTH_DATA")

        #This is the variable that you append raw pressure data to once it is
        #received from the backplane.
        self.raw_pressure_data = []
        self.depth_scaling = [9.2, 9.2]
        self.depth_bias = [606, 95]

        #Initialize Kalman Filter Parameters( Note this needs to be edited per type of transducer and number of transducers)
        #Currently set up for two transducers
        A = np.array([[1]])
        B = np.array([[0]])
        R = np.array([[1e-6]])
        C = np.array([[1],
                      [1]])
        Q = np.array([[1e-5, 0],
                      [0, 1e-5]])

        self.kf = Kalman_Filter(A, B, R, C, Q)

        #Set initial conditions for Kalman filter state
        self.mu = np.array([[0]])
        self.cov = np.array([[10]])

        self.run_thread = True
        self.daemon = True

    def receive_sensor_data(self):
        '''
        Receive the pressure and depth data from the pressure transducers. Fuse
        the data using a Kalman filter to get the best reading

        Parameters:
            N/A

        Returns:
            [pressure, depth]: List of the pressure and depth data if the data
                                is received properly
            False: If the data is not received properly.
        '''

        depths = self._unpack()


        #Perfrom kalman filtering to obtain the most probable pressure and depth
        if(depths == None):
            return None

        #TODO: KALMAN FILTER
        measurement = np.array([[depths[0]], [depths[1]]])
        self.mu, self.cov = self.kf.predict(self.mu, self.cov, np.array([[0]]), measurement)

        depth = self.mu
        #return pressure, depth
        return depth

    def run(self):
        '''
        Continually get pressure and depth data from the pressure transducers and
        publish it to the MechOS network over the topic "TRANS_DATA"

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while self.run_thread:
            try:
                self.data = self.receive_sensor_data()

                if(self.data != None):
                    print(self.data)
                    self.publish_data()


                time.sleep(0.1)

            except Exception as e:
                print("Can't process pressure transducer depth data:", e)



    def _unpack(self):
        '''
        Unpacks the raw depth data sent from the backplane and returns it as
        depth values in feet.

        Parameters:
            N/A

        Returns:
            depths: A list of two depth readings in feet.
            if data is not received properly, return none
        '''
        if(len(self.raw_pressure_data) != 0):
            depths = self.raw_pressure_data.pop(0)
            depths[0] = (1 / self.depth_scaling[0]) * (depths[0] - self.depth_bias[0])
            depths[1] = (1 / self.depth_scaling[1]) * (depths[1] - self.depth_bias[1])

            return depths
        return None
