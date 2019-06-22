'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/25/2019

Description: The sensor driver controls and starts all the threads for each sensor.
             The driver will package up the sensor data into their respective proto
             messages to publish them to the MechOS network for other process to use.
'''
import sys
import os

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

import navigation_data_pb2
import desired_position_pb2
from AHRS import AHRS
from Backplane_Sensor_Data import Backplane_Handler
from DVL import DVL_THREAD
from MechOS import mechos
import serial
import threading
import time
import math

class Sensor_Driver:
    '''
    This is the main sensor driver that gathers and publishes sensor data to the
    mechos network. This includes AHRS, Backplane, Pressure Transducers, and DVL.
    '''
    def __init__(self):
        '''
        Initialize all of the threads for gathering data from each of the sensors.
        This includes AHRS, Backplane, Pressure Transducers, and DVL.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #proto buff packaging
        #self.nav_data_proto = navigation_data_pb2.NAV_DATA()

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Mechos nodes to send Sensor Data
        self.sensor_driver_node = mechos.Node("SENSOR_DRIVER", configs["ip"])
        #self.nav_data_publisher = self.sensor_driver_node.create_publisher("NAV", configs["pub_port"])

        #MechOS node to receive zero position message (zero position message is sent in the DP topic)
        #self.zero_pos_sub = self.sensor_driver_node.create_subscriber("DP", self._zero_pos_callback, configs["sub_port"])
        #self.zero_pos_proto = desired_position_pb2.DESIRED_POS() #Protocol buffer for receiving the zero position flag

        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #Get com ports to connect to sensors
        backplane_com_port = self.param_serv.get_param("COM_Ports/backplane")
        ahrs_com_port = self.param_serv.get_param("COM_Ports/AHRS")
        dvl_com_port = self.param_serv.get_param("COM_Ports/DVL")

        #Initialize the backplane handler
        self.backplane_driver_thread = Backplane_Handler(backplane_com_port)

        #Initialize ahrs handler
        self.ahrs_driver_thread = AHRS(ahrs_com_port)

	    #Initialize DVL thread
        self.dvl_driver_thread = DVL_THREAD(dvl_com_port)

        #Threading lock to access shared thread data safely
        self.threading_lock = threading.Lock()
        self.run_thread = True

        #Start sensor gathering threads
        self.backplane_driver_thread.start()
        self.ahrs_driver_thread.start()
        self.dvl_driver_thread.start()
        self.zero_pos_flag = True

        self.current_x_pos = 0
        self.current_y_pos = 0

    def zero_pos(self):
        '''
        Zero the position of the sub in the x and y coordinates

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.current_x_pos = 0
        self.current_y_pos = 0


    def _get_sensor_data(self):
        '''
        This function is to be used to get the sensor data and return it. It can
        be used if sensor_driver is being imported and NOT used as a thread.

        Parameters:
            N/A
        Returns:
            sensor_data: All the sensor navigation data from AHRS, DVL, and
                    Backplane.
                    form --> [roll, pitch, yaw, x_pos, y_pos, depth]
        '''
        sensor_data = [0, 0, 0, 0, 0, 0]

        #Get the AHRS data
        sensor_data[0:2] = self.ahrs_driver_thread.ahrs_data

        #Get x and y position
        #TODO: Need to move the position estimator to here in the sensor driver
        #DVL returns [x_vel, y_vel, z_vel, x_vel_time_est, y_vel_time_est, z_vel_time_est]
        dvl_data = self.dvl_driver_thread.dvl_data_queue.pop(0)

        #Extract data for better readability
        x_vel, y_vel, z_vel, x_vel_time_est, y_vel_time_est, z_vel_time_est = dvl_data

        yaw_rad = math.radians(sensor_data[2])

        #Rotation matrix to relate sub's x, y coordinates to earth x(north) and y(east) components
        x_translation = ((math.cos(yaw_rad)*x_vel*x_vel_time_est) + \
                        (math.sin(yaw_rad)*y_vel*y_vel_time_est)) * 3.28084

        y_translation = ((-1* math.sin(yaw_rad)*x_vel*x_vel_time_est) + \
                        (math.cos(yaw_rad)*y_vel*y_vel_time_est)) 3.28084 #conver to feet

        self.current_x_pos += x_translation
        self.current_y_pos += y_translation

        sensor_data[3] = self.current_x_pos
        sensor_data[4] = self.current_y_pos

        #Get the depth from the Backplane
        sensor_data[5] = self.backplane_driver_thread.depth_data

        return(sensor_data)

if __name__ == "__main__":

    sensor_driver = Sensor_Driver()
    sensor_driver.run()
