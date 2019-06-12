'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified: 06/12/2019
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
        self.set_up_PID_controllers(True)

    def set_up_PID_controllers(self, initialization=False):
        '''
        Setup the PID controllers with the initial values set in the subs
        parameter xml server file. Also update the strength parameter for
        each thrusters.

        Parameters:
            initialization: If it is the first time that this function is being called,
                            set initialization to true so it creates the pid controllers.
                            If false, it just updates the controller values.

        Returns:
            N/A
        '''
        d_t = float(self.param_serv.get_param("Control/PID/dt"))
        roll_p = float(self.param_serv.get_param("Control/PID/roll_pid/p"))
        roll_i = float(self.param_serv.get_param("Control/PID/roll_pid/i"))
        roll_d = float(self.param_serv.get_param("Control/PID/roll_pid/d"))

        pitch_p = float(self.param_serv.get_param("Control/PID/pitch_pid/p"))
        pitch_i = float(self.param_serv.get_param("Control/PID/pitch_pid/i"))
        pitch_d = float(self.param_serv.get_param("Control/PID/pitch_pid/d"))

        yaw_p = float(self.param_serv.get_param("Control/PID/yaw_pid/p"))
        yaw_i = float(self.param_serv.get_param("Control/PID/yaw_pid/i"))
        yaw_d = float(self.param_serv.get_param("Control/PID/yaw_pid/d"))

        x_p = float(self.param_serv.get_param("Control/PID/x_pid/p"))
        x_i = float(self.param_serv.get_param("Control/PID/x_pid/i"))
        x_d = float(self.param_serv.get_param("Control/PID/x_pid/d"))

        y_p = float(self.param_serv.get_param("Control/PID/y_pid/p"))
        y_i = float(self.param_serv.get_param("Control/PID/y_pid/i"))
        y_d = float(self.param_serv.get_param("Control/PID/y_pid/d"))

        #z = depth pid
        z_p = float(self.param_serv.get_param("Control/PID/z_pid/p"))
        z_i = float(self.param_serv.get_param("Control/PID/z_pid/i"))
        z_d = float(self.param_serv.get_param("Control/PID/z_pid/d"))

        #The bias term is a thruster vale to set to thruster 1, 3, 5, 7 to make the sub neutrally bouyant.
        #This term is added to the proportional gain controller.
        #(K_p * error) + bias
        self.z_bias = float(self.param_serv.get_param("Control/PID/z_pid/bias"))
        self.z_active_bias_depth = float(self.param_serv.get_param("Control/PID/z_pid/active_bias_depth"))

        if(initialization):
            self.roll_pid_controller = PID_Controller(roll_p, roll_i, roll_d, d_t)
            self.pitch_pid_controller = PID_Controller(pitch_p, pitch_i, pitch_d, d_t)
            self.yaw_pid_controller = PID_Controller(yaw_p, yaw_i, yaw_d, d_t)
            self.x_pid_controller = PID_Controller(x_p, x_i, x_d, d_t)
            self.y_pid_controller = PID_Controller(y_p, y_i, y_d, d_t)
            self.z_pid_controller = PID_Controller(z_p, z_i, z_d, d_t)

        else:
            self.roll_pid_controller.set_gains(roll_p, roll_i, roll_d, d_t)
            self.pitch_pid_controller.set_gains(pitch_p, pitch_i, pitch_d, d_t)
            self.yaw_pid_controller.set_gains(yaw_p, yaw_i, yaw_d, d_t)
            self.x_pid_controller.set_gains(x_p, x_i, x_d, d_t)
            self.y_pid_controller.set_gains(y_p, y_i, y_d, d_t)
            self.z_pid_controller.set_gains(z_p, z_i, z_d, d_t)


        #Thruster Strengths (these are used to give more strengths to weeker thrusters in the case that the sub is imbalanced)
        #Each index corresponds to the thruster id.
        self.thruster_strengths = [0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(8):
            param_path = "Control/Thruster_Strengths/T%d" % (i+1)
            self.thruster_strengths[i] = float(self.param_serv.get_param(param_path))
            """
            #The maximum thrust needs to be offset to account for added thruster strength.
            updated_max_thrust = 0
            updated_max_thrust = self.thrusters[i].max_thrust + self.thruster_strengths[i]
            print(updated_max_thrust)
            if(updated_max_thrust > 100):
                updated_max_thrust = 100
                #rint("Updated Thruster %d to have max thrust of %0.2f" % (i, updated_max_thrust))
            self.thrusters[i].max_thrust = updated_max_thrust
            """
        #Get the depth at which the thruster strength offsets will be used (in ft)
        self.thruster_offset_active_depth = float(self.param_serv.get_param("Control/Thruster_Strengths/active_depth"))



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
                        y_control, z_control, curr_z_pos):
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
            curr_z_pos: The current depth position of the sub. This is needed to know
                        when to activate thruster offsets to help hold the sub level.
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

            #Write the thrust to the given thruster. Some thrusters have an additional offset to given them
            #a higher strength. This is used to help balance out weigth distribution issues with the sub.
            if(curr_z_pos >= self.thruster_offset_active_depth):
                thrust = thrust + self.thruster_strengths[thruster_id]

            if(curr_z_pos >= self.z_active_bias_depth):

                thrust = thrust + (self.z_bias * thruster.orientation[2]) #Make sure only thrusters controlling z have this parameter

            self.thrusters[thruster_id].set_thrust(thrust)



    def advance_move(self, current_position, desired_position):
        '''
        Given the current position and desired positions of the AUV, obtain the pid
        control outputs for all 6 degrees of freedom.

        Parameters:
            current_position: A list of the most up-to-date current position.
                            List format: [roll, pitch, yaw, x_pos, y_pos, depth]
            desired_position: A list containing the desired positions of each
                                axis. Same list format as the current_position
                                parameter.

        Returns:
            error: A list of of the errors that where evaluted for each axis.
                    List Format: [roll_error, pitch_error, yaw_error, x_pos_error, y_pos_error, depth_error]
        '''

        #calculate the error of each degree of freedom
        error = [0, 0, 0, 0, 0, 0]

        error[0] = desired_position[0] - current_position[0] #roll error
        error[1] = desired_position[1] - current_position[1] #pitch error

        #Calculate yaw error. The logic includes calculating error for choosing shortest angle to travel
        desired_yaw = desired_position[2]
        curr_yaw = current_position[2]

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
        error[3] = desired_position[3] - current_position[3] #x_pos
        error[4] = desired_position[4] - current_position[4] #y_pos
        error[5] = desired_position[5] - current_position[5] #z_pos (depth)

        #Get the thrusts from the PID controllers to move towards desired pos.
        roll_control = self.roll_pid_controller.control_step(error[0])
        pitch_control = self.pitch_pid_controller.control_step(error[1])
        yaw_control = self.yaw_pid_controller.control_step(error[2])
        x_control = self.x_pid_controller.control_step(error[3])
        y_control = self.y_pid_controller.control_step(error[4])
        z_control = self.z_pid_controller.control_step(error[5])

        #Write the controls to thrusters
        self.controlled_thrust(roll_control, pitch_control, yaw_control, x_control, y_control, z_control)
        return error

    #This is a helper function to be used initially for tuning the roll, pitch
    #and depth PID values. Once tuned, please use advance_move instead.
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
        #print("Current depth position:", curr_z_pos, "Desired_depth_position:", desired_z_pos)
        error[2] = desired_z_pos - curr_z_pos
        z_control = self.z_pid_controller.control_step(error[2])

        #Write controls to thrusters
        #Set x, y, and yaw controls to zero since we don't care about the subs
        #heading or planar orientation for a simple depth move
        self.controlled_thrust(roll_control, pitch_control, 0, 0, 0, z_control, curr_z_pos)

        return error
