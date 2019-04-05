'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/23/2019
Description: This module defines a thread for processing pressure data from two
            pressure transducers and converting/filtering that data to be depth data
'''
import sys
import os

HELPERS_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPERS_PATH)

import time
import struct
import numpy as np
from Kalman_Filter import Kalman_Filter
import threading



class Pressure_Depth_Transducers:
    '''
    Receive Pressure and Depth data from each pressure transducer. Filter the data
    and fuse each sensors data for a less noisey reading using a Kalman Filter.
    '''
    def __init__(self):
        '''
        Initialize communication with each pressure transducer. And set up MechOS
        node to communicate data over the MechOS network.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        #Initialize base classes
        super(Pressure_Depth_Transducers, self).__init__()

        #This is the variable that you append raw pressure data to once it is
        #received from the backplane.
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


    def process_depth_data(self, raw_pressure_data):
        '''
        Receive the pressure and depth data from the pressure transducers. Fuse
        the data using a Kalman filter to get the best reading

        Parameters:
            N/A

        Returns:
            depth: The filtered reading of the current depth
            False: If the data is not received properly.
        '''

        depths = self._unpack(raw_pressure_data)

        #Perfrom kalman filtering to obtain the most probable pressure and depth
        if(depths == None):
            return None

        #TODO: KALMAN FILTER
        measurement = np.array([[depths[0]], [depths[1]]])
        self.mu, self.cov = self.kf.predict(self.mu, self.cov, np.array([[0]]), measurement)

        depth = self.mu
        #return pressure, depth
        return depth

    def _unpack(self, raw_pressure_data):
        '''
        Unpacks the raw depth data sent from the backplane and returns it as
        depth values in feet.

        Parameters:
            N/A

        Returns:
            depths: A list of two depth readings in feet.
            if data is not received properly, return none
        '''
                
        if(raw_pressure_data != None):
            depths = [0, 0]
            depths[0] = (1 / self.depth_scaling[0]) * (raw_pressure_data[0] - self.depth_bias[0])
            depths[1] = (1 / self.depth_scaling[1]) * (raw_pressure_data[1] - self.depth_bias[1])
            self.unfiltered_depth_data = depths
            return depths
        return None
