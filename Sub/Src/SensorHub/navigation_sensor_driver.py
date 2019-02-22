import sys
import os

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

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
    mechos network
    '''
    def __init__(self):
        '''
        Initialize all of the threads for gathering data from each of the sensors.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #proto buff packaging
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()

        #Mechos nodes to send Sensor Data
        self.sensor_driver_node = mechos.Node("SENSOR_DRIVER")
        self.nav_data_publisher = self.sensor_driver_node.create_publisher("NAV")

        self.param_serv = mechos.Parameter_Server_Client()
        parameter_xml_database = os.path.join("..", "Params", "Perseverance.xml")
        parameter_xml_database = os.path.abspath(parameter_xml_database)
        self.param_serv.use_parameter_database(parameter_xml_database)

        #Get com ports to connect to sensors
        backplane_com_port = self.param_serv.get_param("COM_Ports/backplane")
        ahrs_com_port = self.param_serv.get_param("COM_Ports/AHRS")

        #Initialize the backplane handler
        self.backplane_driver_thread = Backplane_Handler(backplane_com_port)

        #Initialize ahrs handler
        self.ahrs_driver_thread = AHRS(ahrs_com_port)

        #Threading lock to access shared thread data safely
        self.threading_lock = threading.Lock()
        self.run_thread = True

        #Start sensor gathering threads
        self.backplane_driver_thread.start()
        self.ahrs_driver_thread.start()

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
                self.nav_data_proto.roll = self.ahrs_driver_thread.ahrs_data[0]
                self.nav_data_proto.pitch = self.ahrs_driver_thread.ahrs_data[1]
                self.nav_data_proto.yaw = self.ahrs_driver_thread.ahrs_data[2]
                self.nav_data_proto.depth = self.backplane_driver_thread.depth_data

                print(self.nav_data_proto)
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
