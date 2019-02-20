'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/08/2019
Description: This module contains a highest level movement controller for Perseverance.
                It contains multiple modes of control for the sub including
                thruster test mode, PID test mode, manual control mode PID,
                autonomous mode PID, LQR test mode, manual control mode LQR, and
                autonomous mode LQR.
'''
import sys
import os
import time

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from position_estimator import Position_Estimator
from movement_pid import Movement_PID
from MechOS import mechos

class Movement_Controller:
    '''
    This main movement controller for the sub. It lets the user select which
    control system to use.
    '''
    def __init__(self):
        '''
        Initialize the movement controller.

        Parameters:
            N/A

        Returns:
            N/A
        '''

        #MechOS node to connect movement controller to mechos network
        self.movement_controller_node = mechos.Node("MOV_CTRL")

        #Subscriber to change movement mode
        self.movement_mode_subscriber = self.movement_controller_node.create_subscriber("MM", self.movement_mode_callback)

        #Initialize the position estimator thread
        self.position_estimator_thread = Position_Estimator()

    def movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which movement controller mode is being used.

        Parameters:
            movement_mode: Raw byte of the mode
        '''
