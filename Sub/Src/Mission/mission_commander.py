import sys
import os
PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from MechOS import mechos
import threading
import time
import json
import serial

#Import all the tasks
from drive_functions import Drive_Functions
from waypoint_task import Waypoint_Task

class Mission_Commander(threading.Thread):
    '''
    Mission Commander is the main controller of the sub's autonomy to execute missions.
    The mission commander will exectue the tasks of a mission from a mission file of type
    '.json'.
    '''

    def __init__(self, mission_file, sensor_driver):
        '''
        Initialize the mission given the mission .json file.
        Parameters:
            mission_file: The path to the .json mission file.
            sensor_driver: The sensor driver thread object so
            the drive functions have access to the sensor data.
        Returns:
            N/A
        '''

        self.mission_file = mission_file
        self.sensor_driver = sensor_driver

        #Initialize the drive functions
        self.drive_functions = Drive_Functions(self.sensor_driver)

        self.mission_tasks = [] #A list of the mission tasks
        self.mission_data = None #The .json file structure loaded into python dictionary

        self.run_thread = True
        self.daemon = True

        self.mission_live = False

        #load the mission data
        self.parse_mission()

    def parse_mission(self):
        '''
        Parse the mission .json file and generate the code for each task. Save
        the individual task in the mission_tasks list attribute.
        Parameters:
            N/A
        Returns:
            N/A
        '''

        with open(self.mission_file, 'r') as f:
            self.mission_data = json.load(f)

        #Count the number of tasks in the mission
        self.num_tasks = len(self.mission_data)
        print("[INFO]: Number of tasks for mission is", num_tasks, ".")

        task_keys = self.mission_data.keys()

        for task_index, task in enumerate(task_keys):

            #Get the task type and name
            task_type = self.mission_data[task]["type"]

            #generate waypoint task
            if(task_type == "Waypoint"):
                waypoint_task = Waypoint_Task(self.mission_data[task], self.drive_functions)
                self.mission_tasks.append(waypoint_task)

    def run(self):
        '''
        Run the mission tasks sequentially.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while(self.run_thread):

            #When mission is live, run the mission
            if(self.mission_live):

                for task_id, task in enumeration(self.mission_tasks):
                    print("[INFO]: Starting Task %s: %s. Mission task %d/%d" %(task.type, task.name, task_id, self.num_tasks))
                    task.run()

if __name__ == "__main__":
    mission_commander = Mission_Commander('MissionFiles/Dummy/mission.json', None)
