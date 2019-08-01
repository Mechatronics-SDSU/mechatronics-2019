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

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from AHRS import AHRS
from Backplane_Sensor_Data import Backplane_Handler
from DVL import DVL_THREAD
from MechOS import mechos
from MechOS.simple_messages.float_array import Float_Array
from MechOS.simple_messages.bool import Bool
import serial
import threading
import time
import math

class Sensor_Driver(threading.Thread):
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

        threading.Thread.__init__(self)
        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Mechos nodes to send Sensor Data
        self.sensor_driver_node = mechos.Node("SENSOR_DRIVER", '192.168.1.14', '192.168.1.14')

        #Publisher to publish the sensor data to the network.
        #Sensd [roll, pitch, yaw, north pos., east pos., depth]
        self.nav_data_publisher = self.sensor_driver_node.create_publisher("SENSOR_DATA",Float_Array(6), protocol="udp", queue_size=1)

        #Subscriber to receive a message to zero position of the currrent north/east position of the sub.
        self.zero_pos_subscriber = self.sensor_driver_node.create_subscriber("ZERO_POSITION", Bool(), self._update_zero_position, protocol="tcp")

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

        self.current_north_pos = 0
        self.current_east_pos = 0

        #Previous time at which the dvl was read, keeps consistent timining of the dvl
        self.prev_dvl_read_time = 0
        self.sensor_data = [0, 0, 0, 0, 0, 0]

        self.run_thread = True
        self.daemon = True

    def _update_zero_position(self, misc):
        '''
        Zero the position of the sub in the x and y coordinates

        Parameters:
            N/A
        Returns:
            N/A
        '''

        self.current_north_pos = 0
        self.current_east_pos = 0


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
        #Get the AHRS data. The ahrs is flipped 180 in the sub, so fix that
        roll, pitch, yaw_flipped = self.ahrs_driver_thread.ahrs_data

        yaw = (yaw_flipped + 180.0) % 360.0

        sensor_data[0:3] = [roll, pitch, yaw]

        #Get x and y position
        #TODO: Need to move the position estimator to here in the sensor driver
        #DVL returns [x_vel, y_vel, z_vel, x_vel_time_est, y_vel_time_est, z_vel_time_est]
        if(len(self.dvl_driver_thread.dvl_data_queue) > 0):
            dvl_data = self.dvl_driver_thread.dvl_data_queue.pop(0)

            #Extract data for better readability
            x_vel, y_vel, z_vel, x_vel_time_est, y_vel_time_est, z_vel_time_est = dvl_data

            yaw_rad = math.radians(sensor_data[2])

            dvl_vel_timing = time.time() - self.prev_dvl_read_time

            #Rotation matrix to relate sub's x, y coordinates to earth x(north) and y(east) components
            #x_translation = ((math.cos(yaw_rad)*x_vel*x_vel_time_est) + \
            #                (math.sin(yaw_rad)*y_vel*y_vel_time_est)) #* 3.28084

            #y_translation = ((-1* math.sin(yaw_rad)*x_vel*x_vel_time_est) + \
            #                (math.cos(yaw_rad)*y_vel*y_vel_time_est)) #* 3.28084 #conver to feet

            #x_translation = ((math.cos(yaw_rad)*x_vel*dvl_vel_timing) + \
            #                (math.sin(yaw_rad)*y_vel*dvl_vel_timing)) * 3.28084

            #y_translation = ((-1* math.sin(yaw_rad)*x_vel*dvl_vel_timing) + \
            #                (math.cos(yaw_rad)*y_vel*dvl_vel_timing)) * 3.28084 #convert to feet

            #FIXED: Rotation matrix was incorrect prior
            x_translation = ((math.cos(yaw_rad)*x_vel*dvl_vel_timing) - \
                            (math.sin(yaw_rad)*y_vel*dvl_vel_timing)) * 3.28084

            y_translation = ((math.sin(yaw_rad)*x_vel*dvl_vel_timing) + \
                            (math.cos(yaw_rad)*y_vel*dvl_vel_timing)) * 3.28084 #convert to feet

            #Get the current times
            self.prev_dvl_read_time = time.time()

            self.current_north_pos += x_translation
            self.current_east_pos += y_translation
        sensor_data[3] = self.current_north_pos
        sensor_data[4] = self.current_east_pos

        #Get the depth from the Backplane
        sensor_data[5] = self.backplane_driver_thread.depth_data
        return(sensor_data)

    def run(self):
        '''
        If sensor driver is to be run as it's own thread, this is the run function
        that it will execute.

        Parameters:
            N/A
        Returns:
            N/A
        '''

        while(self.run_thread):

            try:
                self.sensor_driver_node.spin_once()
                sensor_data = self._get_sensor_data()

                if(sensor_data != None):
                    self.sensor_data = sensor_data

                self.nav_data_publisher.publish(self.sensor_data)


            except Exception as e:
                print("[ERROR]: Sensor Driver could not correctly collect sensor data. Error:", e)

            time.sleep(0.01)



if __name__ == "__main__":

    sensor_driver = Sensor_Driver()
    sensor_driver.run()
