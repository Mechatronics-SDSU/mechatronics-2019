import sys
import os

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

MESSAGE_TYPES_PATH = os.path.join("..", "..", "..", "Message_Types")
sys.path.append(MESSAGE_TYPES_PATH)
from neural_network_message import Neural_Network_Message

from MechOS import mechos
from MechOS.simple_messages.int import Int
from MechOS.simple_messages.bool import Bool
from MechOS.simple_messages.float_array import Float_Array

import threading
import time
import json
import serial
import struct
#Import all the tasks
from drive_functions import Drive_Functions
from waypoint_task import Waypoint_Task
from gate_no_vision_task import Gate_No_Vision_Task
from initial_dive_task import Initial_Dive_Task
from buoy_task import Buoy_Task

class Mission_Commander(threading.Thread):
    '''
    Mission Commander is the main controller of the sub's autonomy to execute missions.
    The mission commander will exectue the tasks of a mission from a mission file of type
    '.json'.
    '''

    def __init__(self):
        '''
        Initialize the mission given the mission .json file.
        Parameters:
            sensor_driver: The sensor driver thread object so
            the drive functions have access to the sensor data.
        Returns:
            N/A
        '''

        threading.Thread.__init__(self)

        self.mission_file = None

        #Initialize the drive functions
        self.drive_functions = Drive_Functions()

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Connect to parameters server
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #MechOS node to connect the mission commander to the mechos network
        self.mission_commander_node = mechos.Node("MISSION_COMMANDER", '192.168.1.14', '192.168.1.14')

        #subscriber to listen if the movement mode is set to be autonomous mission mode
        self.movement_mode_subscriber = self.mission_commander_node.create_subscriber("MOVEMENT_MODE", Int(), self._update_movement_mode_callback, protocol="tcp")
        #subscriber to listen if the mission informatin has changed.
        self.update_mission_info_subscriber = self.mission_commander_node.create_subscriber("MISSON_SELECT", Bool(), self._update_mission_info_callback, protocol="tcp")
        #subscriber to listen if neural network data is available
        self.neural_network_subscriber = self.mission_commander_node.create_subscriber("NEURAL_NET", Neural_Network_Message(), self._update_neural_net_callback, protocol="tcp")

        self.neural_net_data = [0, 0, 0, 0, 0, 0]

        #Publisher to be able to kill the sub within the mission
        self.kill_sub_publisher = self.mission_commander_node.create_publisher("KILL_SUB", Bool(), protocol="tcp")

        #Publisher to zero the position of the sub.
        self.zero_position_publisher = self.mission_commander_node.create_publisher("ZERO_POSITION", Bool(), protocol="tcp")

        #Set up serial com to read the autonomous button
        com_port = self.param_serv.get_param("COM_Ports/auto")
        self.auto_serial = serial.Serial(com_port, 9600)

        #Set up a thread to listen to request from the GUI
        self.command_listener_thread = threading.Thread(target=self._command_listener)
        self.command_listener_thread.daemon = True
        self.command_listener_thread_run = True
        self.command_listener_thread.start()

        self.mission_tasks = [] #A list of the mission tasks
        self.mission_data = None #The .json file structure loaded into python dictionary

        self.run_thread = True
        self.daemon = True

        self.mission_mode = False #If true, then the subs navigation system is ready for missions
        self.mission_live = False  #Mission live corresponds to the autonomous buttons state.

        #Variable to keep the current sensor data(position) of the sub.
        self.current_position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


        #load the mission data
        self._update_mission_info_callback(None)

    def _update_mission_info_callback(self, misc):
        '''
        If the update mission info button is pressed in the mission planner widget,
        update the mission info here. Note that the mission being live should go to
        false.

        Parameters:
            misc: Nothing used.
        Returns:
            N/A
        '''

        #Get the new mission file from the parameter server.
        self.mission_file = self.param_serv.get_param("Missions/mission_file")
        self.mission_live = False

        print("[INFO]: New Mission file set as %s" % self.mission_file)
        #Parse the mission file
        self.parse_mission()

    def _update_movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which navigation controller mode is being used.
        If it is set to 3, then the navigation controller is ready for autonomous mode.
        Parameters:
            movement_mode: Raw byte of the mode.
        Returns:
            N/A
        '''
        if(movement_mode == 3):
            print("[INFO]: Mission Commander Ready to Run Missions. Sub Initially Killed")

            #Initially have the sub killed when switched to mission commander mode
            self.kill_sub_publisher.publish(1)

            self.mission_mode = True

        else:

            if(self.mission_mode == True):
                print("[INFO]: Exited Mission Command Mode.")

            self.mission_mode = False
            self.mission_live = False
            self.drive_functions.drive_functions_enabled = False

    def _update_neural_net_callback(self, neural_net_data):
        self.neural_net_data = neural_net_data
        print(self.neural_net_data)

    def _command_listener(self):
        '''
        The thread to run update requests from the GUI to tell the mission commander
        when it is ready to run missions and what missions to do.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while self.command_listener_thread_run:
            try:
                #Recieve commands from the the GUI and/or Mission Commander
                self.mission_commander_node.spin_once()

                if(self.auto_serial.in_waiting):
                    auto_pressed = (self.auto_serial.read(13)).decode()
                    self.auto_serial.read(2) #Read the excess two bytes
                    print(auto_pressed)
                    if(auto_pressed == "Auto Status:1" and self.mission_mode):
                        print("[INFO]: Mission Now Live")
                        self.mission_live = True
                        self.drive_functions.drive_functions_enabled = True

                    elif(auto_pressed == "Auto Status:0" and self.mission_mode):
                        print("[INFO]: Mission is no longer Live.")
                        self.mission_live = False
                        self.drive_functions.drive_functions_enabled = False

            except Exception as e:
                print("[ERROR]: Could not properly recieved messages in command listener. Error:", e)
            time.sleep(0.001)

    def parse_mission(self):
        '''
        Parse the mission .json file and generate the code for each task. Save
        the individual task in the mission_tasks list attribute.
        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.mission_tasks = [] #Reset the mission tasks
        with open(self.mission_file, 'r') as f:
            self.mission_data = json.load(f)

        #Count the number of tasks in the mission
        self.num_tasks = len(self.mission_data)
        print("[INFO]: Parsing Mission. Number of tasks for mission is", self.num_tasks, ".")

        task_keys = self.mission_data.keys()

        for task_index, task in enumerate(task_keys):

            #Get the task type and name
            task_type = self.mission_data[task]["type"]

            if(task_type == "Initial_Dive"):
                initial_dive_task = Initial_Dive_Task(self.mission_data[task], self.drive_functions)
                self.mission_tasks.append(initial_dive_task)

            #generate waypoint task
            elif(task_type == "Waypoint"):
                waypoint_task = Waypoint_Task(self.mission_data[task], self.drive_functions)
                self.mission_tasks.append(waypoint_task)

            #Generate Gate with no vision task
            elif(task_type == "Gate_No_Vision"):
                gate_no_vision = Gate_No_Vision_Task(self.mission_data[task], self.drive_functions)
                self.mission_tasks.append(gate_no_vision)
            '''
            elif(task_type == "Buoy_Mission"):
                buoy_task = Buoy_Task(self.mission_data[task], self.drive_functions, self.neural_net_data)
                self.mission_tasks.append(buoy_task)
            '''

    def run(self):
        '''
        Run the mission tasks sequentially.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while(self.run_thread):

            try:
                #If in Mission mode, listen to see if the autonomous mode button is
                #pressed.

                if(self.mission_mode and self.mission_live):

                    #self.mission_live = True
                    print("[INFO]: Starting Mission")
                    #When mission is live, run the mission
                    #Unkill the sub
                    self.kill_sub_publisher.publish(False)

                    #Zero position of the sensors
                    self.zero_position_publisher.publish(True)
                    time.sleep(0.1) #wait for the messae to make it
                    #Iterate through each task in the mission and run them
                    for task_id, task in enumerate(self.mission_tasks):
                        if((self.mission_live == False) or (self.mission_mode == False)):
                            print("[WARNING]: Exiting mission because mission live status or mission mode status changed.")
                            break

                        print("[INFO]: Starting Task %s: %s. Mission task %d/%d" %(task.type, task.name, task_id + 1, self.num_tasks))
                        task_success = task.run()
                        if(task_success):
                            print("[INFO]: Successfully completed task %s." % task.name)
                            continue
                        else:
                            print("[INFO]: Failed to complete task %s." % task.name)

                    print("[INFO]: Finished Mission. Killing the sub.")
                    self.mission_live = False

                    #Kill the sub.
                    self.kill_sub_publisher.publish(True)
            except:
                print("[ERROR]: Encountered an Error in Mission Commander. Error:", sys.exc_info()[0])
                raise



if __name__ == "__main__":
    mission_commander = Mission_Commander()
    mission_commander.run()
