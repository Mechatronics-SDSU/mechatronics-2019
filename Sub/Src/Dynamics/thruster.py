'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/30/2019

Description: This module contains the "Thruster" class which allows control of thruster
            speeds using PWM.
'''
import sys
import os

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

import numpy as np
from MechOS import mechos
import serial
import time
import struct
import copy

class Thruster():
    '''
    This class defines an object for individual thrusters. It let's you set the speed (and direction)
    of the thrusters. Setting the PWM signal will actually send the comman to the thruster.
    '''

    def __init__(self, maestro_serial_obj, thruster_id, orientation, location, max_thrust, invert_thruster=False):
        '''
        Initialize settings for individual thruster.

        Parameters:
            maestro_serial_obj: The open serial communication port object connected
                                to the maestro motor controller.
            thruster_id: An int id value assigned to individual thrusters. Most
                        AUV's have thrusters assigned 1 - 8.
            orientation: A 3 element long list specifying the direction in which the
                        thruster controls. Typically thrusters control thruster in either
                        x, y, or z direction. Hence the list is in the form of
                        [x, y, z]. For example, if the given thruster controls the x direction,
                        its orientation should be [1, 0, 0].
            location: The physical location of the thruste with respect to the center of the
                        sub (as unit vectors). The center of the sub is considered the origin.
                        Again the list form is [x, y, z]. 'x' correspondes to the axis running
                        from the front to the back of the sub. 'y' corresponds to the axis
                        running left to right side of the sub. And 'z' corresponds to the
                        axis running from the bottom to the top of the sub.
            max_thrust: A value between 0 and 100 signifying the maximum thrust possible. Example,
                        80 would mean limiting the thruster to 80% it's maximum possible thrust at
                        all times
            invert_thruster: A boolean expression to allow the direction of the thrusters to be changed
                                in the software. If true, the thruster will spin in the opposite direction
        '''
        self.maestro_serial_obj = maestro_serial_obj
        self.thruster_id = thruster_id
        self.orientation = orientation
        self.location = location
        self.max_thrust = max_thrust
        self.invert_thruster = 1
        if(invert_thruster):
            self.invert_thruster = -1

        #remember the previous thrust value set in so you do not keep sending the same thrust value
        self.previous_thrust= None

    def set_thrust(self, thrust):
        '''
        Set the thrust value of the thruster and it to the maestro to drive the thruster.
        The thruster values will be bounded by the maximum thrust value.

        Parameters:
            thrust: At thrust value in the range of [-100, 100]. Where -100 is maximum reverse
            thrust and 100 is maximum normal direction thrust.

        Returns:
            N/A
        '''
        #Will change the direction of the thruster if necessary
        thrust = self.invert_thruster * thrust

        if thrust != self.previous_thrust:

            if thrust > self.max_thrust:
                self.previous_thrust = copy.copy(self.max_thrust)


                #Re-bound thrust from [-100, 100] to [0, 255] for writing PWM signal
                thrust = int(np.interp(self.max_thrust, [-100, 100], [0, 254]))

            elif thrust < (-1*self.max_thrust):

                self.previous_thurst = copy.copy(-self.max_thrust)

                thrust = int(np.interp(-self.max_thrust, [-100, 100], [0, 254]))

            else:
                self.previous_thrust = thrust

                thrust = int(np.interp(thrust, [-100, 100], [0, 254]))

            #write thrust to maestro
            self.maestro_serial_obj.write(bytearray([0xFF, self.thruster_id, thrust]))
