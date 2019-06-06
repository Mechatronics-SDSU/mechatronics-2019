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

MOVEMENT_CONT_PATH = os.path.join("..", "Dynamics")
sys.path.append(MOVEMENT_CONT_PATH)
from movement_controller import Movement_Controller
import time

class Main_Controller:
    '''
    '''
    def __init__(self):
        '''
        Intialize the main controller of the sub.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #Initialize the sensor driver. This will start
        #the threads to collect sensor data.
        #self.sensor_controller = Sensor_Driver()

        #Initialize the movement controller thread
        self.movement_controller = Movement_Controller()

        self.run_main_controller = True

        #Start up threads
        #Start the movement controller
        self.movement_controller.start()

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
    main_controller = Main_Controller()
    main_controller.run()

