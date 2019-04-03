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
from AHRS import AHRS
from Backplane_Sensor_Data import Backplane_Handler
from MechOS import mechos
import serial
import threading
import time

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
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Mechos nodes to send Sensor Data
        self.sensor_driver_node = mechos.Node("SENSOR_DRIVER", configs["ip"])
        self.nav_data_publisher = self.sensor_driver_node.create_publisher("NAV", configs["pub_port"])

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

	#iNITIALIZE dvl DRIVER THREAD
	self.dvl_driver_thread = DVL_THREAD(dvl_com_port)

        #Threading lock to access shared thread data safely
        self.threading_lock = threading.Lock()
        self.run_thread = True

        #Start sensor gathering threads
        self.backplane_driver_thread.start()
        self.ahrs_driver_thread.start()
	self.dvl_driver_thread.start()

    def run(self):
        '''
        Main thread loop that packages the sensor data from the other sensors into
        a protobuf and pushlishes it to the mechos network.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while(self.run_thread):

            try:
		
                #Put data from sensor threads into proto sturcture
		
		ahrs_data_packet = self.ahrs_driver_thread.ahrs_data
		self.nav_data_proto.roll = ahrs_data_packet[0]
                self.nav_data_proto.pitch = ahrs_data_packet[1]
                self.nav_data_proto.yaw = ahrs_data_packet[2]

                self.nav_data_proto.depth = self.backplane_driver_thread.depth_data
		
		
		dvl_data_packet = self.dvl_driver_thread.PACKET
		self.nav_data_proto.x_translation = dvl_data_packet[4]
		self.nav_data_proto.y_translation = dvl_data_packet[5]

                #print(self.nav_data_proto)
                #Serialize data in proto to send
                serialized_nav_data = self.nav_data_proto.SerializeToString()
                #publish navigation data
                self.nav_data_publisher.publish(serialized_nav_data)

            except Exception as e:
                print("Couldn't publish sensor data:", e)

            time.sleep(0.1)
if __name__ == "__main__":

    sensor_driver = Sensor_Driver()
    sensor_driver.run()
