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

#Import all the missions
from Drive import Drive

class Mission_Commander:
    '''
    Mission Commander is the main controller of the sub's autonomy to execute missions.
    The mission commander will generate the missions from a mission file of type '.json'.
    '''
    
    def __init__(self, mission_file):
        '''
        Initialize the mission given the mission .json file.

        Parameters:
            mission_file: The path to the .json mission file.

        Returns:
            N/A
        '''
        self.mission_file = mission_file
        
        #Initialize MechOS node
        #Get the mechos network parameters
        """
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        self.mission_commander_node = mechos.Node("MISSION_COMMANDER", configs["ip"])

        #Navigation data provides the current position
        self.nav_data_subscriber = self.mission_commander_node.create_subscriber("NAV", self._update_nav_data, configs["sub_port"])
        self.desired_pos_publisher = self.mission_commander_node.create_publisher("DP", configs["pub_port"])

        #Initialize the protobuf messages for receiving navigation data
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()
        
        #Create thread to continually listen for navigation data
        self.nav_data_listener_thread = threading.Thread(target=self._update_nav_data_thread)
        self.nav_data_listener_thread.daemon = True
        self.nav_data_listener_thread.start() #Start the thread
        """
        self.current_pos = [0, 0, 0, 0, 0, 0]

        self.mission_tasks = []
        self.mission_data = [] #The .json file structure loaded into python dictionary

        #load the mission data
        self.parse_mission()

    def _update_nav_data(self, nav_data_proto):
        '''
        This is the callback function for the navigation data subscriber.
        De-serialize the navigation data proto and save it to 
        self.current_pos attribute.

        Parameters:
            nav_data_proto: A serialized navigation data protobuf message 
                    of type NAV_DATA().
        Returns:
            N/A
        '''
        #De-serialized
        self.nav_data_proto.ParseFromString(nav_data_proto)

        self.current_pos[0] = self.nav_data_proto.roll
        self.current_pos[1] = self.nav_data_proto.pitch
        self.current_pos[2] = self.nav_data_proto.yaw
        self.current_pos[3] = self.nav_data_proto.x_absolute_pos
        self.current_pos[4] = self.nav_data_proto.y_absolute_pos
        self.current_pos[5] = self.nav_data_proto.depth
        
    def _update_nav_data_thread(self):
        '''
        Continually receive current navigation data by calling the
        subscribers spinOnce function.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while True:
            self.nav_data_subscriber.spinOnce()
            time.sleep(0.1)

    def parse_mission(self):
        '''
        Parse the mission .json file and generate the code for each task. Save
        the individual task in the mission_tasks list attribute.

        Parameters:
            N/A
        Returns:
            N/A
        '''

        pos_params = ["roll", "pitch", "yaw", "x_pos", "y_pos", "depth"]
        with open(self.mission_file, 'r') as f:
            self.mission_data = json.load(f)

        #Count the number of tasks in the mission
        num_tasks = len(self.mission_data)
        print("Number of tasks for mission is", num_tasks, ".")

        task_keys = self.mission_data.keys()

        for task_index, task in enumerate(task_keys):
            #Get the task type and name
            task_type = self.mission_data[task]["type"]
            task_name = self.mission_data[task]["name"]

            if(task_type == "Drive"): #Generate the object for performing the drive mission
                
                timeout = self.mission_data[task]["timeout"]
                buffer_zone = self.mission_data[task]["buffer_zone"]
                wait_time = self.mission_data[task]["wait_time"]
                pos_ref = self.mission_data[task]["pos_ref"]

                #Load the desired position parameters
                desired_pos = [0, 0, 0, 0, 0, 0]
                for index, pos_axis in enumerate(pos_params):
                    desired_pos[index] = self.mission_data[task]["desired_pos"][pos_axis]
                
                #load the data into the Drive object
                self.mission_tasks.append(Drive(self, desired_pos, wait_time, buffer_zone, task_name, timeout,
                                        pos_ref))
                self.mission_tasks[-1].print_task_information()

if __name__ == "__main__":
    mission_commander = Mission_Commander('mission_example.json')
