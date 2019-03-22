'''
Author: Mohammad Shafi
Last modified: 03/21/2019
Description: This is a helper script to calibrate depth properly. It sets the bias
to the depth the sub reads at 0, and calculates depth accordingly. It then publishes
this data to the paramter server.
References: sensor_driver.py, Backplane_Sensor_Data.py by David Pierce Walker Howell
'''

import sys
import os

BACKPLANE_PATH = os.path.join("..", "SensorHub")
sys.path.append(BACKPLANE_PATH)

import numpy as np
import threading
import serial
import time
from Backplane_Sensor_Data import Backplane_Handler
from MechOS import mechos

class Depth_Calibrator:
    '''
    Initializes depth calibrator object. Use this to create connection to backplane, establish
    Mechatronics parameter server connection, and ensure that we are receiving backplane data
    '''
    def __init__(self):
        self.param_serv = mechos.Parameter_Server_Client()
        parameter_xml_database = os.path.join("..", "Params", "Perseverance.xml")
        parameter_xml_database = os.path.abspath(parameter_xml_database)
        self.param_serv.use_parameter_database(parameter_xml_database)

        backplane_com_port = self.param_serv.get_param("COM_Ports/backplane")
        self.backplane_driver_thread = Backplane_Handler(backplane_com_port)
        self.threading_lock = threading.Lock()
        self.run_thread = True

        self.backplane_driver_thread.start()

def calculate_depth(input, offset):
    '''
    This function calculates our depth scale. The equation we use is as follows:
    user input = (raw pressure data - bias)/depth scale. The user input is the depth we want the sub to
    submerge to, while the bias is a running average of our raw pressure data we are receiving
    at 0.
    '''
    depth_scale = np.array([(offset[0] / input), (offset[1] / input)])
    return depth_scale

if __name__ == '__main__':
    '''
    A lot going on in main. First, a Depth Calibrator object is created, to initialize connections and
    have a paramater server clinet running connected to MechOS. Next, a running average of pressure data at 0
    is calculated, which we take as our bias. We then find the depth scale by calling the depth scale function
    above. Afterward, everything is updated on Percy's xml parameter database under Sensors.
    '''
    depth_calibrator = Depth_Calibrator()
    user_input = int(input("Enter the depth you want the sub to submerge to: "))
    raw_pressure_data_x = 0
    raw_pressure_data_y = 0
    for x in range(0, 100):
        raw_pressure_data_x = raw_pressure_data_x + depth_calibrator.backplane_driver_thread.depth_processing.raw_depth_data[0]
        raw_pressure_data_y = raw_pressure_data_y + depth_calibrator.backplane_driver_thread.depth_processing.raw_depth_data[1]

    offset = np.array([(raw_pressure_data_x/100), (raw_pressure_data_y/100)])
    print(offset)
    depth_scale = calculate_depth(user_input, offset)
    print(depth_scale)
    depth_calibrator.param_serv.set_param("Sensors/trans_1_scaling", str(depth_scale[0]))
    depth_calibrator.param_serv.set_param("Sensors/trans_2_scaling", str(depth_scale[1]))
    depth_calibrator.param_serv.set_param("Sensors/trans_1_bias", str(offset[0]))
    depth_calibrator.param_serv.set_param("Sensors/trans_2_bias", str(offset[1]))
    time.sleep(0.1)
    #Todo: return this depth_scale back to Kalman_Filter?
