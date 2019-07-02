'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 06/5/2019

Description: The main process on the sub that will orchatrate
            everything. This includes the control system, sensor driver,
            and mission commander. Also controls communication with the GUI.
'''
import sys
import os

#SENSOR_HUB_PATH = os.path.join("..", "SensorHub")
#sys.path.append(SENSOR_HUB_PATH)
#from sensor_driver import Sensor_Driver

NAV_CONT_PATH = os.path.join("..", "Dynamics")
sys.path.append(NAV_CONT_PATH)
from navigation_controller import Navigation_Controller

SENSOR_HUB_PATH = os.path.join("..", "SensorHub")
sys.path.append(SENSOR_HUB_PATH)
from sensor_driver import Sensor_Driver

from message_passing.Nodes.node_base_udp import node_base
import time
import socket

class Main_Controller(node_base):
    '''
    '''
    def __init__(self, MEM, IP):
        '''
        Intialize the main controller of the sub.

        Parameters:
            MEM: local dictionary containing all data for local message transfer
            IP: dictionary containing address, sockets, etc for network transfer

        Returns:
            N/A
        '''
        #Initialize the sensor driver. This will start
        #the threads to collect sensor data.
        #self.sensor_controller = Sensor_Driver()

        node_base.__init__(self, MEM, IP)
        self._memory = MEM
        self._ip_route = IP

        self.sensor_driver = Sensor_Driver()
        self.navigation_controller = Navigation_Controller(MEM, IP, self.sensor_driver)

        self.run_main_controller = True
       
        #Start up threads
        self.sensor_driver.start()
        self.navigation_controller.start()

    def print_sensor_data(self, sensor_data):
        '''
        Format and print out the sensor data to the command window.

        Parameters:
            sensor_data: A list of the sensor data.
                        [roll, pitch, yaw, x_pos, y_pos, depth]

        Returns:
            N/A
        '''
        if(sensor_data == None):
            print("Sensor Data Currently Unavailable to display")
            return

        print("\nRoll: %0.2f" % (sensor_data[0]))
        print("Pitch: %0.2f" % (sensor_data[1]))
        print("Yaw: %0.2f" % (sensor_data[2]))
        print("X Pos.: %0.2f" % (sensor_data[3]))
        print("Y Pos.: %0.2f" % (sensor_data[4]))
        print("Depth: %0.2f" % (sensor_data[5]))

    def run(self):
        '''
        Run the Main controller of the sub
        '''
        while(self.run_main_controller):
            continue

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
    MEM={'RC':b'\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00'}

    main_controller = Main_Controller(MEM, IP)
    main_controller.start()
