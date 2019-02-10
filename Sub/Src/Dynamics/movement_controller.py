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
from protoFactory import packageProtobuf
import Mechatronics_pb2

from movement_pid import Movement_PID
from MechOS import mechos

class Movement_Controller:
    '''
    '''
    def __init__(self):
        '''
        '''
        #DEVELOPE BETTER INITIALIZATION SOLUTION
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.depth = 0

        #Initialize parameter server client
        self.param_serv = mechos.Parameter_Server_Client()
        parameter_xml_database = os.path.join("..", "Params", "Perseverance.xml")
        parameter_xml_database = os.path.abspath(parameter_xml_database)
        self.param_serv.use_parameter_database(parameter_xml_database)

        #Initialize the mechos node
        self.movement_controller_node = mechos.Node("MOVEMENT_CONTROLLER")

        self.proto_decoder = Mechatronics_pb2.Mechatronics()

        #Setup mechos subscribers and proto decoders
        #Thruster test
        self.thruster_test_sub = self.movement_controller_node.create_subscriber("THRUST",
                                                        self._thruster_test)

        #Mode selection subscriber
        self.movement_mode_sub = self.movement_controller_node.create_subscriber("MOV_MODE",
                                                       self._set_movement_mode)

        self.movement_mode = self.param_serv.get_param("Control/Movement_Mode/default")

        #AHRS,DVL, PRESSURE SENSOR subscribers
        self.AHRS_sub = self.movement_controller_node.create_subscriber("AHRS_DATA",
                                                        self._extract_sensor_data)
        self.DVL_sub = self.movement_controller_node.create_subscriber("DVL_DATA",
                                                        self._extract_sensor_data)
        self.depth_sub = self.movement_controller_node.create_subscriber("DEPTH_DATA",
                                                        self._extract_sensor_data)

        #Subscriber for PID value change
        self.PID_sub = self.movement_controller_node.create_subscriber("PIDS",
                                                        self._set_pid_values)

        self.PID_error_pub = self.movement_controller_node.create_publisher("PID_ERRORS")

        #PID based movement controller
        self.movement_pid_controller = Movement_PID(self.PID_error_pub)

    def _set_movement_mode(self, movement_mode):
        '''
        Call back function from MechOS subscriber listening for a change in movement
        mode.

        Parameters:
            movement_mode: One of the following string values representing the mode
                        selection.

                    '0' -> Thruster Test Mode
                    '1' -> PID Test/Tuning Mode
                    '2' -> Manual Control Mode (PID)
                    '3' -> Autonomous Control Mode (PID)
                    '4' -> LQR Test/Tuning Mode
                    '5' -> Manual Control Mode (LQR)
                    '6' -> Autonomous Control Mode (LQR)
        '''
        self.movement_mode = str(movement_mode)


    def _thruster_test(self, thrust_proto_data):
        '''
        Call back function for the test thruster subscriber. Thruster tests are
        only done when the movement controller is in thruster test mode

        Parameters:
            thrust_proto_data: A proto buff message containging data under type
                                thruster.

        Returns:
            N/A
        '''
        self.proto_decoder.ParseFromString(thrust_proto_data)
        thrusts = [self.proto_decoder.thruster.thruster_1,
                   self.proto_decoder.thruster.thruster_2,
                   self.proto_decoder.thruster.thruster_3,
                   self.proto_decoder.thruster.thruster_4,
                   self.proto_decoder.thruster.thruster_5,
                   self.proto_decoder.thruster.thruster_6,
                   self.proto_decoder.thruster.thruster_7,
                   self.proto_decoder.thruster.thruster_8]


        self.movement_pid_controller.simple_thrust(thrusts)

    def _extract_sensor_data(self, proto_sensor_data):
        '''
        '''
        self.proto_decoder.ParseFromString(proto_sensor_data)

        #AHRS data
        if(self.proto_decoder.type == Mechatronics_pb2.AHRS_DATA):
            self.roll = self.proto_decoder.ahrs.roll
            self.pitch = self.proto_decoder.ahrs.pitch
            self.yaw = self.proto_decoder.ahrs.yaw

        elif(self.proto_decoder.type == Mechatronics_pb2.PRESSURE_TRANSDUCERS):
            self.depth = self.proto_decoder.pressureTrans.depth

    def _set_pid_values(self, pid_proto):
        '''
        '''
        self.proto_decoder.ParseFromString(pid_proto)
        k_p = self.proto_decoder.pid.k_p
        k_i = self.proto_decoder.pid.k_i
        k_d = self.proto_decoder.pid.k_d

        #Roll pid
        if(self.proto_decoder.pid.PID_channel == 0):
            #Update gain values for roll pid
            self.movement_pid_controller.roll_pid_controller.set_gains(k_p, k_i, k_d)

        elif(self.proto_decoder.pid.PID_channel == 0):
            #Update gain values for pitch pid
            self.movement_pid_controller.pitch_pid_controller.set_gains(k_p, k_i, k_d)

        elif(self.proto_decoder.pid.PID_channel == 0):
            #Update gain values for yaw pid
            self.movement_pid_controller.yaw_pid_controller.set_gains(k_p, k_i, k_d)

        elif(self.proto_decoder.pid.PID_channel == 0):
            #Update gain values for x pid
            self.movement_pid_controller.x_pid_controller.set_gains(k_p, k_i, k_d)

        elif(self.proto_decoder.pid.PID_channel == 0):
            #Update gain values for y pid
            self.movement_pid_controller.y_pid_controller.set_gains(k_p, k_i, k_d)

        else(self.proto_decoder.pid.PID_channel == 0):
            #Update gain values for z pid
            self.movement_pid_controller.z_pid_controller.set_gains(k_p, k_i, k_d)


    def run(self):
        '''
        '''
        while(True):

            #Check if operator is requesting to change movement mode
            self.movement_controller_node.spinOnce(self.movement_mode_sub)

            #Thruster Test Mode
            if(self.movement_mode == '0'):

                self.movement_controller_node.spinOnce(self.thruster_test_sub)

            #PID tuning mode
            elif(self.movement_mode == '1'):
                #Get data from AHRS, DVL, and pressure transducers (for depth)
                self.movement_controller_node.spinOnce(self.AHRS_sub)
                self.movement_controller_node.spinOnce(self.DVL_sub)
                self.movement_controller_node.spinOnce(self.depth_sub)
                self.movement_controller_node.spinOnce(self.PID_sub)


                self.movement_pid_controller.simple_depth_move_no_yaw(self.roll,
                                            self.pitch, self.depth, 0, 0, 3)

        time.sleep(0.01)



if __name__ == "__main__":
    movement_controller = Movement_Controller()
    movement_controller.run()
