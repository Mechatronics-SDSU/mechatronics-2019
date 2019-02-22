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
import desired_position_pb2

from position_estimator import Position_Estimator
from movement_pid import Movement_PID
from MechOS import mechos
import struct

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
        self.desired_position_subscriber = self.movement_controller_node.create_subscriber("DP", self.unpack_desired_position_callback)

        #Initialize the position estimator thread
        self.position_estimator_thread = Position_Estimator()
        self.position_estimator_thread.start()

        #Default movement mode should be PID autonomy
        self.movement_mode = '0'
        self.run_thread = True

        #Initialize PID controller
        self.pid_controller = Movement_PID()

        #Initialial desired position
        self.desired_position = [0, 0, 0, 0, 0, 0]
        self.desired_position_proto = desired_position_pb2.DESIRED_POS()

    def movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which movement controller mode is being used.

        Parameters:
            movement_mode: Raw byte of the mode.

        Returns:
            N/A
        '''
        self.movement_mode = struct.unpack('s', movement_mode)
    def unpack_desired_position_callback(self, desired_position_proto):
        '''
        The callback function to unpack the desired position proto message received
        through MechOS.

        Parameters:
            desired_position_proto: Protobuf of type DESIRED_POS to unpack

        Returns:
            N/A
        '''
        self.desired_position_proto.ParseFromString(desired_position_proto)
        self.desired_position[0] = self.desired_position_proto.roll
        self.desired_position[1] = self.desired_position_proto.pitch
        self.desired_position[2] = self.desired_position_proto.yaw
        self.desired_position[3] = self.desired_position_proto.depth
        self.desired_position[4] = self.desired_position_proto.x_pos
        self.desired_position[5] = self.desired_position_proto.y_pos

    def run(self):
        '''
        Runs the movement control in the control mode specified by the user.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        current_position = [0, 0, 0, 0, 0, 0]

        while(self.run_thread):

            #Poll movement mode subscriber to see if user changed control mode
            self.movement_controller_node.spinOnce(self.movement_mode_subscriber)

            #PID Autonomy mode
            if self.movement_mode == '0':

                #Currently, the movement mode only test a simple PID depth move
                current_position = self.position_estimator_thread.belief_position

                #Get the desired position of the sub
                self.movement_controller_node.spineOnce(self.unpack_desired_position_callback)

                #Perform movement to desired position
                self.pid_controller.simple_depth_move_no_yaw(current_position[0],
                                                             currnet_position[1],
                                                             current_position[3],
                                                             self.desired_position[0],
                                                             self.desired_position[1],
                                                             self.desired_position[3])

            time.sleep(0.1)

if __name__ == "__main__":
    movement_controller = Movement_Controller()

    movement_controller.run()
