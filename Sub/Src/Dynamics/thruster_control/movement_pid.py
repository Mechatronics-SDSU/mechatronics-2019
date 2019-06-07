'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/25/2019
Description: This module contains a PID based movement controller that is used
            to control the six degrees of freedom control of Perseverance.
'''
import sys
import os

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

from thruster import Thruster
from pid_controller import PID_Controller
from MechOS import mechos
import serial

class Movement_PID:
    '''
    A movement controller for Perseverance that relies on PID controller to control
    the 6 degrees of freedom.
    '''

    def __init__(self):
        '''
        Initialize the thrusters and PID controllers on Perseverance.

        Parameters:
            error_publisher: A MechOS publisher to send the publish the current error

        Returns:
            N/A
        '''
        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Initialize parameter server client to get and set parameters related to
        #the PID controller. This includes update time and PID contstants for
        #each degree of freedom.
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #Initialize serial connection to the maestro
        com_port = self.param_serv.get_param("COM_Ports/maestro")
        maestro_serial_obj = serial.Serial(com_port, 9600)

        #Initialize all 8 thrusters (max thrust 80%)
        max_thrust = float(self.param_serv.get_param("Control/max_thrust"))

        self.thrusters = [None, None, None, None, None, None, None, None]
        self.thrusters[0] = Thruster(maestro_serial_obj, 1, [0, 0, 1], [1, -1, 0], max_thrust, True)
        self.thrusters[1] = Thruster(maestro_serial_obj, 2, [0, 1, 0], [1, 0, 0], max_thrust, False)
        self.thrusters[2] = Thruster(maestro_serial_obj, 3, [0, 0, 1], [1, 1, 0], max_thrust, False)
        self.thrusters[3] = Thruster(maestro_serial_obj, 4, [1, 0, 0], [0, 1, 0], max_thrust, False)
        self.thrusters[4] = Thruster(maestro_serial_obj, 5, [0, 0, 1], [-1, 1, 0], max_thrust, True)
        self.thrusters[5] = Thruster(maestro_serial_obj, 6, [0, 1, 0], [-1, 0, 0], max_thrust, False)
        self.thrusters[6] = Thruster(maestro_serial_obj, 7, [0, 0, 1], [-1, -1, 0], max_thrust, False)
        self.thrusters[7] = Thruster(maestro_serial_obj, 8, [1, 0, 0], [0, -1, 0], max_thrust, False)


        #Initialize the PID controllers for control system
        self.set_up_PID_controllers()

    def set_up_PID_controllers(self):
        '''
        Setup the PID controllers with the initial values set in the subs
        parameter xml server file.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        d_t = float(self.param_serv.get_param("Control/PID/dt"))
        roll_p = float(self.param_serv.get_param("Control/PID/roll_pid/p"))
        roll_i = float(self.param_serv.get_param("Control/PID/roll_pid/i"))
        roll_d = float(self.param_serv.get_param("Control/PID/roll_pid/d"))
        self.roll_pid_controller = PID_Controller(roll_p, roll_i, roll_d, d_t)

        pitch_p = float(self.param_serv.get_param("Control/PID/pitch_pid/p"))
        pitch_i = float(self.param_serv.get_param("Control/PID/pitch_pid/i"))
        pitch_d = float(self.param_serv.get_param("Control/PID/pitch_pid/d"))
        self.pitch_pid_controller = PID_Controller(pitch_p, pitch_i, pitch_d, d_t)

        yaw_p = float(self.param_serv.get_param("Control/PID/yaw_pid/p"))
        yaw_i = float(self.param_serv.get_param("Control/PID/yaw_pid/i"))
        yaw_d = float(self.param_serv.get_param("Control/PID/yaw_pid/d"))
        self.yaw_pid_controller = PID_Controller(yaw_p, yaw_i, yaw_d, d_t)

        x_p = float(self.param_serv.get_param("Control/PID/x_pid/p"))
        x_i = float(self.param_serv.get_param("Control/PID/x_pid/i"))
        x_d = float(self.param_serv.get_param("Control/PID/x_pid/d"))
        self.x_pid_controller = PID_Controller(x_p, x_i, x_d, d_t)

        y_p = float(self.param_serv.get_param("Control/PID/y_pid/p"))
        y_i = float(self.param_serv.get_param("Control/PID/y_pid/i"))
        y_d = float(self.param_serv.get_param("Control/PID/y_pid/d"))
        self.y_pid_controller = PID_Controller(y_p, y_i, y_d, d_t)

        #z = depth pid
        z_p = float(self.param_serv.get_param("Control/PID/z_pid/p"))
        z_i = float(self.param_serv.get_param("Control/PID/z_pid/i"))
        z_d = float(self.param_serv.get_param("Control/PID/z_pid/d"))
        self.z_pid_controller = PID_Controller(z_p, z_i, z_d, d_t)

    def simple_thrust(self, thrusts):
        '''
        Individually sets each thruster PWM given the PWMs in the thrusts
        list.

        Parameters:
            thrusts: A list of length 8 containing a thrust value (%) between
            [-100, 100]. The list should be in order of the thruster ids.

        Returns:
            N/A
        '''

        for thruster_id, thrust in enumerate(thrusts):
            self.thrusters[thruster_id].set_thrust(thrust)

    def controlled_thrust(self, roll_control, pitch_control, yaw_control, x_control,
                        y_control, z_control):
        '''
        Function takes control outputs from calculated by the PID values and applys
        them to the 6 degree control matrix to determine the thrust for each thruster
        to reach desired point.

        Parameters:
            roll_control: The control output from the roll pid controller.
            pitch_control: The control output from the pitch pid controller.
            yaw_control: The control output from the yaw pid controller.
            x_control: The control output from the x translation pid controller.
            y_control: The control output from the y translation pid controller.
            z_control: The control output from the z translation pid controller.

        Returns:
            N/A
        '''
        for thruster_id, thruster in enumerate(self.thrusters):

            thrust = (roll_control * thruster.orientation[2] * thruster.location[1]) + \
                     (pitch_control * thruster.orientation[2] * thruster.location[0]) + \
                     (yaw_control * thruster.orientation[1] * thruster.location[0]) + \
                     (yaw_control * thruster.orientation[0] * thruster.location[1]) + \
                     (x_control * thruster.orientation[0]) + \
                     (y_control * thruster.orientation[1]) + \
                     (z_control * thruster.orientation[2])
            self.thrusters[thruster_id].set_thrust(thrust)

    def advance_move(self, curr_roll, curr_pitch, curr_yaw, curr_x_pos, curr_y_pos,
                    curr_z_pos, desired_roll, desired_pitch, desired_yaw,
                    desired_x_pos, desired_y_pos, desired_z_pos):
        '''
        Given the current position and desired positions of the AUV, obtain the pid
        control outputs for all 6 degrees of freedom.

        Parameters:
            curr_roll: Current roll data
            curr_pitch Current pitch data
            curr_yaw: Current yaw data
            curr_x_pos: Current x position
            curr_y_pos: Current y position
            curr_z_pos: Current z position
            desired_roll: Desired roll position
            desired_pitch: Desired pitch position
            desired_yaw: Desired yaw position
            desired_x_pos: Desired x position
            desired_y_pos: Desired y position
            desired_z_pos: Desired z position

        Returns:
            N/A
        '''

        #calculate the error of each degree of freedom
        error = [0, 0, 0, 0, 0, 0]

        error[0] = desired_roll - curr_roll #roll error
        error[1] = desired_pitch - curr_pitch #pitch error

        #Calculate yaw error. The logic includes calculating error for choosing shortest angle to travel
        if(desired_yaw >= curr_yaw):
            yaw_error = desired_yaw - curr_yaw
            if(yaw_error > 180):    #This will choose the shortest angle to take to desred position.
                error[2] = yaw_error - 360
            else:
                error[2] = yaw_error

        else:
            yaw_error = curr_yaw - desired_yaw
            if(abs(yaw_error) > 180):
                error[2] = yaw_error + 360
            else:
                error[2] = yaw_error

        #Calculate translation error
        error[3] = desired_z_pos - curr_z_pos
        error[4] = desired_x_pos - curr_x_pos
        error[5] = desired_y_pos - curr_y_pos

        roll_control = self.roll_pid_controller.control_step(error[0])
        pitch_control = self.pitch_pid_controller.control_step(error[1])
        yaw_control = self.yaw_pid_controller.control_step(error[2])
        z_control = self.z_pid_controller.control_step(error[3])
        x_control = self.x_pid_controller.control_step(error[4])
        z_control = self.z_pid_controller.control_step(error[5])

        #Write the contrls to thrusters
        self.controlled_thrust(roll_control, pitch_control, yaw_control, x_control, y_control, z_control)
        return error


    def simple_depth_move_no_yaw(self, curr_roll, curr_pitch,curr_z_pos,
                          desired_roll, desired_pitch, desired_z_pos):
        '''
        Without carrying about x axis position, y axis position, or yaw, use the PID controllers
        to go down to a give depth (desired_z_pos) with a give orientation.

        Parameters:
            curr_roll: Current roll data
            curr_pitch Current pitch data
            curr_z_pos: Current z position
            desired_roll: Desired roll position
            desired_pitch: Desired pitch position
            desired_z_pos: Desired z (depth) position

        Returns:
            error: The roll, pitch and depth error
        '''
        #Calculate error for each degree of freedom
        error = [0, 0, 0, 0, 0, 0]
        error[0] = desired_roll - curr_roll
        roll_control = self.roll_pid_controller.control_step(error[0])

        error[1] = desired_pitch - curr_pitch
        pitch_control = self.pitch_pid_controller.control_step(error[1])

        #depth error
        print(curr_z_pos, desired_z_pos)
        error[2] = desired_z_pos - curr_z_pos
        z_control = self.z_pid_controller.control_step(error[2])

        #Write controls to thrusters
        #Set x, y, and yaw controls to zero since we don't care about the subs
        #heading or planar orientation for a simple depth move
        self.controlled_thrust(roll_control, pitch_control, 0, 0, 0, z_control)

        return error
