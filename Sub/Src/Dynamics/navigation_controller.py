
'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Collaborator: Mohammad Shafi <ma.shafi99@gmail.com>
Last Modified 06/16/2019
Description: This module contains a highest level navigation controller for Perseverance.
                It contains multiple modes of control for the sub including
                thruster test mode, PID test mode, and Autonomous control mode.
'''
import sys
import os
import time

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

SENSOR_HUB_PATH = os.path.join("..", "SensorHub")
sys.path.append(SENSOR_HUB_PATH)
from sensor_driver import Sensor_Driver

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

from movement_pid import Movement_PID
from MechOS import mechos
import struct
import threading

from message_passing.Nodes.node_base_udp import node_base
import socket

MOVEMENT_AXIS = ["Roll", "Pitch", "Yaw", "X Pos.", "Y Pos.", "Depth"]

class Navigation_Controller(node_base):
    '''
    This main Navigation controller for the sub. It is made up of two main components.
    This first main is the sensor driver, which provides navigation data from the sensor.
    The second component is the movement controller components, which controls the movement
    pid control system. There is also a command_listener that listens for requests from the gui/mission commander.
    '''
    def __init__(self, MEM, IP):
        '''
        Initialize the navigation controller. This includes getting parameters from the
        parameter server, initializing subscribers to listen for command messages, and
        initalizing the sensor driver.

        Parameters:
            MEM: Local dictionary needed to send data over RAM
            IP: Dictionary containing addresses, sockets, and everything needed
                to send over the network

        Returns:
            N/A
        '''

        #Node base initialized stuff, necessary for socket communication
        node_base.__init__(self, MEM, IP)
        self._memory = MEM
        self._ip_route = IP

        #Initialize the parent class of
        super(Navigation_Controller, self).__init__(MEM, IP)

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS node to connect movement controller to mechos network
        self.navigation_controller_node = mechos.Node("MOV_CTRL", configs["ip"])

        #Subscriber to change movement mode
        self.movement_mode_subscriber = self.navigation_controller_node.create_subscriber("MM", self.__update_movement_mode_callback, configs["sub_port"])

        #Update PID configurations button
        self.pid_configs_subscriber = self.navigation_controller_node.create_subscriber("PID", self.__update_pid_configs_callback, configs["sub_port"])

        #Subscriber to get the desired position set by the user/mission controller.
        self.desired_position_subscriber = self.navigation_controller_node.create_subscriber("DP", self.__unpack_desired_position_callback, configs["sub_port"])

        #TODO: Create a thread that publishes the errors
        #Publisher that published the PID errors for each degree of freedom
        self.pid_errors_proto = pid_errors_pb2.PID_ERRORS()
        self.pid_errors_publisher = self.navigation_controller_node.create_publisher("PE", configs["pub_port"])
        self.update_pid_errors = False
        self.pid_values_update_freeze = True #Boolean to be used if the movement controller should check for updated PID values.

        #Subscriber to listen for thrust messages from the thruster test widget
        self.thruster_test_subscriber = self.navigation_controller_node.create_subscriber("TT", self.__update_thruster_test_callback, configs["sub_port"])
        self.thruster_test_proto = thrusters_pb2.Thrusters() #Thruster protobuf message

        self._udp_received_message = None

        #Connect to parameters server
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #Initialize the sensor driver, which will run all the threads to recieve
        #sensor data.
        self.sensor_driver = Sensor_Driver()

        #Publisher to send the sensor data/current position/navigation data to the GUI and Mission Commander
        self.nav_data_publisher = self.navigation_controller_node.create_publisher("NAV", configs["pub_port"])
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()

        #Subscriber to commands from the GUI and Mission commanderto listen if the sub is killed.
        self.sub_killed_subscriber = self.navigation_controller_node.create_subscriber("KS", self._update_sub_killed_state, configs["sub_port"])


        #Get navigation controller timing
        self.nav_time_interval = float(self.param_serv.get_param("Timing/nav_controller"))
        self.nav_timer = util_timer.Timer()

        #Initial movement mode to match GUI.
        #0 --> PID tuner
        #1 --> Thruster tester
        self.movement_mode = 0

        #Allow the naviagtion controller thread to run
        self.run_thread = True

        #1--> Thrusters are softkilled (by software)
        #0--> Thrusters are unkilled and can be commanded.
        self.sub_killed = 1

        #Initialize 6 degree of freedom PID movement controller used for the sub.
        #Primary control system for the sub
        self.pid_controller = Movement_PID()

        #Initialize current position [roll, pitch, yaw, north_pos, east_pos, depth]
        self.current_position = [0, 0, 0, 0, 0, 0]
        self.pos_error = [0, 0, 0, 0, 0, 0] #errors for all axies

        #Initialize desired position [roll, pitch, yaw, north_pos, east_pos, depth]
        self.desired_position = [0, 0, 0, 0, 0, 0]
        self.desired_position_proto = desired_position_pb2.DESIRED_POS()

        #Set up a thread to listen to a requests from GUI/mission_commander.
        # This includes movement mode, desired_position, new PID values, and sub killed command.
        self.command_listener_thread = threading.Thread(target=self._command_listener)
        self.command_listener_thread.daemon = True
        self.command_listener_thread_run = True
        self.command_listener_thread.start()

        #A thread to update the GUI/mission commander on the current position of the sub
        # and the current PID errors if the sub is in PID tunning mode
        self.update_command_thread = threading.Thread(target=self._update_command)
        self.update_command_thread.daemon = True
        self.update_command_thread_run = True
        self.update_command_thread.start()

        self.remote_thread= threading.Thread(target=self._read_remote_control)
        self.remote_commands = [0.0, 0.0, 0.0, 0.0, 0]
        self.remote_thread.daemon = True
        self.remote_control_listen = False
        self.remote_thread.start()

        self.daemon = True

        print("[INFO]: Sub Initially Killed")

    def _update_sub_killed_state(self, killed_state):
        '''
        The callback function to update the sub_killed state if the sub kill/unkill
        button is pressed. Updates the self.sub_killed attribute

        Parameters:
            killed_state: Raw byte (representing a boolean) for if the sub should
                            be killed or unkilled.
        Returns:
            N/A
        '''

        self.sub_killed = struct.unpack('b', killed_state)[0]
        print("[INFO]: Sub Killed:", bool(self.sub_killed))

    def __update_movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which movement controller mode is being used.
        It does this by setting the movment_mode class attribute. Updates the self.movement_mode
        attribute.

        Parameters:
            movement_mode: Raw byte of the mode.

        Returns:
            N/A
        '''

        self.movement_mode = struct.unpack('b', movement_mode)[0]
        if(self.movement_mode == 0):
            print("[INFO]: Movement mode selected: PID Tuner Mode.")
            self.pid_values_update_freeze = False

            #SET TRUE IF YOU WANT TO GRAPHICALLY OBSERVE THE PID ERRORS IN THE GUI.
            self.update_pid_errors = False
            self.remote_hold_depth_state = False

        elif(self.movement_mode == 1):
            print("[INFO]: Movement mode selected: Thruster Test Mode")
            self.pid_values_update_freeze = True
            self.update_pid_errors = False
            self.remote_hold_depth_state = False

        elif(self.movement_mode == 2):
            print("[INFO]: Movement mode selected: Remote Control Mode")
            self.remote_control_listen = True
            self.pid_values_update_freeze = True
            self.update_pid_errors = False

    def __update_pid_configs_callback(self, misc):
        '''
        The callback function to update the pid configuration if the save button
        is pressed. Calls the update pid values function of movement_pid.py.

        Parameters:
            misc: This parameter is not passed anything of value, because if this function
                    is called then it should just update the PID's.
        Returns:
            N/A
        '''
        self.pid_controller.set_up_PID_controllers()

    def _read_remote_control(self):
        '''
        The thread to continuosly read data from the Xbox controller when in
        remote control mode.
        '''
        #Recieve commands via socket from remote controller
        while True:
            if self.remote_control_listen:
                self._udp_received_message = self._recv('RC', local = False)
                self.remote_commands = struct.unpack('ffff???', self._udp_received_message)
            else:
                time.sleep(0.01)

    def _command_listener(self):
        '''
        The thread to run to update requests from the gui or mission commaner for changes in the movement mode,
        sub_killed, and desired position. Also send the current sensor data to the GUI and mission commander.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while self.command_listener_thread_run:
            try:
                #Recieve commands from the the GUI and/or Mission Commander
                self.navigation_controller_node.spinOnce(self.movement_mode_subscriber)
                self.navigation_controller_node.spinOnce(self.sub_killed_subscriber)
                self.navigation_controller_node.spinOnce(self.desired_position_subscriber)

                #If pid values update is not frozen, then update the pid values from the parameter server.
                if(self.pid_values_update_freeze == False):
                    self.navigation_controller_node.spinOnce(self.pid_configs_subscriber)
            except Exception as e:
                print("[ERROR]: Could not properly recieved messages in command listener. Error:", e)
            time.sleep(0.2)

    def _update_command(self):
        '''
        This thread publishes the sensor data which gives the current naviagtion position to
        the GUI and Mission Commander. It also sends the current PID error if in PID tuning mode.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while(self.update_command_thread_run):
            try:
                #Package up the sensor data in protobuf to be published
                self.nav_data_proto.roll = self.current_position[0]
                self.nav_data_proto.pitch = self.current_position[1]
                self.nav_data_proto.yaw = self.current_position[2]
                #TODO:Uncomment to get x and y positions.
                self.nav_data_proto.north_pos = self.current_position[3]
                self.nav_data_proto.east_pos = self.current_position[4]
                self.nav_data_proto.depth = self.current_position[5]

                serialized_nav_data = self.nav_data_proto.SerializeToString()
                self.nav_data_publisher.publish(serialized_nav_data) #Send the current position

                #TODO: Uncomment if you would like to recieve the position errors.
                if(self.update_pid_errors):
                    #Package PID error protos
                    #self.pid_errors_proto.roll_error = self.pos_error[0]
                    #self.pid_errors_proto.pitch_error = self.pos_error[1]
                    #self.pid_errors_proto.yaw_error = self.pos_error[2]
                    #self.pid_errors_proto.north_pos_error = self.pos_error[3]
                    #self.pid_errors_proto.east_pos_error = self.pos_error[4]
                    #self.pid_errors_proto.z_pos_error = self.pos_error[5] #depth error

                    serialzed_pid_errors_proto = self.pid_errors_proto.SerializeToString()
                    self.pid_errors_publisher.publish(serialzed_pid_errors_proto)
            except Exception as e:
                print("[ERROR]: Could not correctly send data from navigation controller. Error:", e)
            time.sleep(0.1)

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
        self.desired_position[3] = self.desired_position_proto.north_pos
        self.desired_position[4] = self.desired_position_proto.east_pos
        self.desired_position[5] = self.desired_position_proto.depth

        if(self.desired_position_proto.zero_pos):
            self.sensor_driver.zero_pos()

        print("\n\nNew Desire Position Recieved:")
        for index, dp in enumerate(self.desired_position):
            print("%s: %0.2f" % (MOVEMENT_AXIS[index], dp), end='')
        print("")


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

        print("\nTesting Thrusters")
        for index, value in enumerate(thrusts):
            print("Thruster %d: %d%% " % (index, value),end='')
        print("")
        self.pid_controller.simple_thrust(thrusts)


    def run(self):
        '''
        Runs the movement control in the control mode specified by the user. The
        different modes of control are as follows.

            '0' --> PID tunning mode.
            '1' --> Thruster test mode.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        current_position = [0, 0, 0, 0, 0, 0]
        self.nav_timer.restart_timer()

        while(self.run_thread):

            nav_time = self.nav_timer.net_timer()

            if(nav_time < self.nav_time_interval):
                time.sleep(self.nav_time_interval - nav_time)
                self.nav_timer.restart_timer()
            else:
                self.nav_timer.restart_timer()
            #Get the current position form sensor driver
            current_position = self.sensor_driver._get_sensor_data()

            if(current_position != None):
                self.current_position = current_position

            if(self.sub_killed == 1):
                #Turn off all thrusters
                self.pid_controller.simple_thrust([0, 0, 0, 0, 0, 0, 0, 0])


            #PID Depth, pitch, roll Tunning Mode
            #In PID depth, pitch, roll tunning mode, only roll pitch and depth are used in
            #the control loop perfrom a simpe Depth PID move. north_pos, east_pos, and
            #yaw are ignored.
            elif self.movement_mode == 0:


                #----SIMPLE DEPTH MOVE NO YAW--------------------------------------
                #NOTE: USED ONLY FOR PID TUNNING AND TESTING PURPOSES.
                #Perform the PID control step to move the sub to the desired depth
                #The error received is the roll, pitch, and depth error
                # error = self.pid_controller.simple_depth_move_no_yaw(self.current_position[0],
                #                                              self.current_position[1],
                #                                              self.current_position[5],
                #                                              self.desired_position[0],
                #                                              self.desired_position[1],
                #                                              self.desired_position[5])
                # self.pos_error[0] = error[0]
                # self.pos_error[1] = error[1]
                # self.pos_error[5] = error[2]
                #----------------------------------------------------------------------

                #----ADVANCE MOVE (ALL 6 DEGREES OF FREEDOMW)--------------------------
                self.pos_error = self.pid_controller.advance_move(self.current_position, self.desired_position)

            #THRUSTER test mode.
            elif self.movement_mode == 1:

                self.navigation_controller_node.spinOnce(self.thruster_test_subscriber)

            #Remote navigation (using PID controllers)
            elif self.movement_mode == 2: #SWITCHED MOVMENT MODES FOR TESTING CONTROLLER, REVERT BACK

                self.pid_controller.remote_move(self.current_position, self.remote_commands)

if __name__ == "__main__":

    rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('192.168.1.14', 6312)
    thrust_socket.bind((ip_address))

    IP={'RC':
            {
            'address': ip_address,
            'sockets': (rc_socket, thrust_socket),
            'type': 'UDP'
            }
        }
    MEM={'RC':b'irrelevant'}

    navigation_controller = Navigation_Controller(MEM, IP)
    navigation_controller.start()
