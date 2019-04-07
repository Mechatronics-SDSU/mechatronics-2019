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

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import desired_position_pb2
import pid_errors_pb2
import navigation_data_pb2
import thrusters_pb2

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
        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS node to connect movement controller to mechos network
        self.movement_controller_node = mechos.Node("MOV_CTRL", configs["ip"])

        #Subscriber to change movement mode
        self.movement_mode_subscriber = self.movement_controller_node.create_subscriber("MM", self.__update_movement_mode_callback, configs["sub_port"])

        #Subscriber to get the desired position set by the user/mission controller.
        self.desired_position_subscriber = self.movement_controller_node.create_subscriber("DP", self.__unpack_desired_position_callback, configs["sub_port"])
        self.pid_errors_proto = pid_errors_pb2.PID_ERRORS()

        #Publisher that published the PID errors for each degree of freedom
        self.pid_errors_publisher = self.movement_controller_node.create_publisher("PE", configs["pub_port"])

        #Subscriber to listen for thrust messages from the thruster test widget
        self.thruster_test_subscriber = self.movement_controller_node.create_subscriber("TT", self.__update_thruster_test_callback, configs["sub_port"])
        self.thruster_test_proto = thrusters_pb2.Thrusters() #Thruster protobuf message

        #Connect to parameters server
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #TODO: Remove Position Estimator from Dynamics
        #Initialize the position estimator thread. The position estimator
        #will estimate the real time current position of the sub with respect to
        #the origin set.
        #self.position_estimator_thread = Position_Estimator()
        #self.position_estimator_thread.start()

        #Proto buffer containing all of the navigation data
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()
        self.current_position_subscriber = self.movement_controller_node.create_subscriber("NAV", self.__get_position_callback, configs["sub_port"])


        #Get movement controller timing
        self.time_interval = float(self.param_serv.get_param("Timing/movement_control"))

        self.movement_mode = 1
        self.run_thread = True

        #Initialize 6 degree of freedom PID movement controller used for the sub.
        self.pid_controller = Movement_PID()

        #Initialize current position
        self.current_position = [0, 0, 0, 0, 0, 0]

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

        #Set up a thread to listen to a movement mode change.
        self.movement_mode_thread = threading.Thread(target=self.update_movement_mode_thread)
        self.movement_mode_thread.daemon = True
        self.movement_mode_thread_run = True
        self.movement_mode_thread.start()

    def __update_movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which movement controller mode is being used.
        It does this by setting the movment_mode class attribute

        Parameters:
            movement_mode: Raw byte of the mode.

        Returns:
            N/A
        '''

        self.movement_mode = struct.unpack('b', movement_mode)[0]

    def update_movement_mode_thread(self):
        '''
        The thread to run to update listen for changes in the movement mode. Started by a
        thread.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while self.movement_mode_thread_run:

            self.movement_controller_node.spinOnce(self.movement_mode_subscriber)
            time.sleep(0.2)
    def __get_position_callback(self, nav_data_proto):
        '''
        The callback function to unpack the navigation data sent from the sensor driver.

        Parameter:
            nav_data_proto: Protobuf of type NAV_DATA to unpack

        Returns:
            N/A
        '''
        self.nav_data_proto.ParseFromString(nav_data_proto)
        self.current_position[0] = self.nav_data_proto.roll
        self.current_position[1] = self.nav_data_proto.pitch
        self.current_position[2] = self.nav_data_proto.yaw
        self.current_position[3] = self.nav_data_proto.depth
        self.current_position[4] = self.nav_data_proto.x_translation
        self.current_position[5] = self.nav_data_proto.y_translation

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

    def __update_thruster_test_callback(self, thruster_proto):
        '''
        The callback function to unpack and write thrusts to each thruster for
        thruster test.

        Parameters:
            thruster_proto: Protobuf of type Thrusters.

        Returns:
            N/A
        '''
        self.thruster_test_proto.ParseFromString(thruster_proto)

        thrusts = [0, 0, 0, 0, 0, 0, 0, 0]
        thrusts[0] = self.thruster_test_proto.thruster_1
        thrusts[1] = self.thruster_test_proto.thruster_2
        thrusts[2] = self.thruster_test_proto.thruster_3
        thrusts[3] = self.thruster_test_proto.thruster_4
        thrusts[4] = self.thruster_test_proto.thruster_5
        thrusts[5] = self.thruster_test_proto.thruster_6
        thrusts[6] = self.thruster_test_proto.thruster_7
        thrusts[7] = self.thruster_test_proto.thruster_8
        print(thrusts)
        self.pid_controller.simple_thrust(thrusts)


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

            #PID Depth, pitch, roll Tunning Mode
            #In PID depth, pitch, roll tunning mode, only roll pitch and depth are used in
            #the control loop perfrom a simpe Depth PID move. x_pos, y_pos, and
            #yaw are ignored.
            if self.movement_mode == 0:

                if(self.pid_values_update_thread_run == False):
                    self.pid_values_update_thread_run = True
                    self.pid_values_update_thread.start()

                #TODO: Remove Position Estimator from Dynamics
                #The current position (roll, pitch, yaw, depth, x_disp, y_disp)
                #calculated by the position estimator thread.
                #current_position = self.position_estimator_thread.belief_position
                self.movement_controller_node.spinOnce(self.current_position_subscriber)

                #Get the desired position of the sub. Typically this message is
                #sent from the GUI or mission controller.
                self.movement_controller_node.spinOnce(self.desired_position_subscriber)

                #print(current_position, self.desired_position)

                #----SIMPLE DEPTH MOVE NO YAW--------------------------------------
                #Perform the PID control step to move the sub to the desired depth
                #The error received is the roll, pitch, and depth error
                error = self.pid_controller.simple_depth_move_no_yaw(self.current_position[0],
                                                             self.current_position[1],
                                                             self.current_position[3],
                                                             self.desired_position[0],
                                                             self.desired_position[1],
                                                             self.desired_position[3])
                #Package PID error protos
                self.pid_errors_proto.roll_error = error[0]
                self.pid_errors_proto.pitch_error = error[1]
                self.pid_errors_proto.z_pos_error = error[2] #depth error
                print(self.pid_errors_proto)
                serialzed_pid_errors_proto = self.pid_errors_proto.SerializeToString()
                self.pid_errors_publisher.publish(serialzed_pid_errors_proto)
                #----------------------------------------------------------------------

                #----ADVANCE MOVE (ALL 6 DEGREES OF FREEDOMW)--------------------------
                #error = self.pid_controller.advance_move(self.current_position[0], 
                #                                        self.current_position[1], 
                #                                        self.current_position[2],
                #                                        self.current_position[4],
                #                                        self.current_position[5],
                #                                        self.current_position[3])
            
                #self.pid_errors_proto.roll_error = error[0]
                #self.pid_errors_proto.pitch_error = error[1]
                #self.pid_errors_proto.yaw_error = error[2]
                #self.pid_errors_proto.x_pos_error = error[4]
                #self.pid_errors_proto.y_pos_error = error[5]
                #self.pid_errors_proto.z_pos_error = error[6]
                #---------------------------------------------------------------------
            #THRUSTER test mode.
            elif self.movement_mode == 1:

                self.movement_controller_node.spinOnce(self.thruster_test_subscriber)

            time.sleep(self.time_interval)

if __name__ == "__main__":
    movement_controller = Movement_Controller()

    movement_controller.run()
