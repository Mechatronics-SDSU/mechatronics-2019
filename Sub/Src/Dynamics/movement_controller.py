'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/25/2019
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
import threading

class Movement_Controller:
    '''
    This main movement controller for the sub. It lets the user select which
    control system to is currently used to move and balance the sub.
    '''
    def __init__(self):
        '''
        Initialize the movement controller. This includes connecting publishers
        and subscribers to the MechOS network to configure and control the movement
        operation.

        Parameters:
            N/A

        Returns:
            N/A
        '''

        #MechOS node to connect movement controller to mechos network
        self.movement_controller_node = mechos.Node("MOV_CTRL")

        #Subscriber to change movement mode
        self.movement_mode_subscriber = self.movement_controller_node.create_subscriber("MM", self.__update_movement_mode_callback)

        #Subscriber to get the desired position set by the user/mission controller.
        self.desired_position_subscriber = self.movement_controller_node.create_subscriber("DP", self.__unpack_desired_position_callback)

        #Connect to parameters server
        self.param_serv = mechos.Parameter_Server_Client()
        parameter_xml_database = os.path.join("..", "Params", "Perseverance.xml")
        parameter_xml_database = os.path.abspath(parameter_xml_database)
        self.param_serv.use_parameter_database(parameter_xml_database)

        #Initialize the position estimator thread. The position estimator
        #will estimate the real time current position of the sub with respect to
        #the origin set.
        self.position_estimator_thread = Position_Estimator()
        self.position_estimator_thread.start()


        self.movement_mode = '1'
        self.run_thread = True

        #Initialize 6 degree of freedom PID movement controller used for the sub.
        self.pid_controller = Movement_PID()

        #Initialize desired position
        self.desired_position = [0, 0, 0, 0, 0, 0]
        self.desired_position_proto = desired_position_pb2.DESIRED_POS()

        #Set up thread to update PID values. The GUI has the ability to change
        #the proportional, integral, and derivative constants by setting them in
        #the parameter server. These values should only be checked in the PID tunning
        #modes.
        self.pid_values_update_thread = threading.Thread(target=self.__update_pid_values)
        self.pid_values_update_thread.daemon = True
        self.pid_values_update_thread_run = False


    def __update_movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which movement controller mode is being used.
        It does this by setting the movment_mode class attribute

        Parameters:
            movement_mode: Raw byte of the mode.

        Returns:
            N/A
        '''
        self.movement_mode = struct.unpack('s', movement_mode)

    def __unpack_desired_position_callback(self, desired_position_proto):
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

    def __update_pid_values(self):
        '''
        Call the RPC server to check if new PID values have been updated.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while(self.pid_values_update_thread_run):
            #Checks the parameters server to obtain possible new PID constants
            #for every control degree of freedom.
            self.pid_controller.set_up_PID_controllers()
            time.sleep(0.1)


    def run(self):
        '''
        Runs the movement control in the control mode specified by the user. The
        different modes of control are as follows.

            '0' --> Thruster test mode.
            '1' --> Roll, Pitch, Depth PID tunning mode.
            '2' --> PID tunning mode. Tunes all 6 degrees of freedom PID controls

        Parameters:
            N/A

        Returns:
            N/A
        '''
        current_position = [0, 0, 0, 0, 0, 0]

        while(self.run_thread):

            #Poll movement mode subscriber to see if user changed control mode
            self.movement_controller_node.spinOnce(self.movement_mode_subscriber)

            #PID Depth, pitch, roll Tunning Mode
            #In PID depth, pitch, roll tunning mode, only roll pitch and depth are used in
            #the control loop perfrom a simpe Depth PID move. x_pos, y_pos, and
            #yaw are ignored.
            if self.movement_mode == '1':

                if(self.pid_values_update_thread_run == False):
                    self.pid_values_update_thread_run = True
                    self.pid_values_update_thread.start()

                #The current position (roll, pitch, yaw, depth, x_disp, y_disp)
                #calculated by the position estimator thread.
                current_position = self.position_estimator_thread.belief_position

                #Get the desired position of the sub. Typically this message is
                #sent from the GUI or mission controller.
                self.movement_controller_node.spinOnce(self.desired_position_subscriber)

                print(current_position, self.desired_position)

                #Perform the PID control step to move the sub to the desired depth
                self.pid_controller.simple_depth_move_no_yaw(current_position[0],
                                                             current_position[1],
                                                             current_position[3],
                                                             self.desired_position[0],
                                                             self.desired_position[1],
                                                             self.desired_position[3])

            time.sleep(0.1)

if __name__ == "__main__":
    movement_controller = Movement_Controller()

    movement_controller.run()
