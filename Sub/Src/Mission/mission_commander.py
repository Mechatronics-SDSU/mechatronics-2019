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

        self.current_pos[0, 0, 0, 0, 0, 0]

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
    