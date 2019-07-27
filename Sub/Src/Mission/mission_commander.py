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
import struct
#Import all the tasks
from drive_functions import Drive_Functions
from waypoint_task import Waypoint_Task
from gate_no_vision_task import Gate_No_Vision_Task

class Mission_Commander(threading.Thread):
    '''
    Mission Commander is the main controller of the sub's autonomy to execute missions.
    The mission commander will exectue the tasks of a mission from a mission file of type
    '.json'.
    '''

    def __init__(self, sensor_driver):
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
        self.sensor_driver = sensor_driver

        #Initialize the drive functions
        self.drive_functions = Drive_Functions(self.sensor_driver)

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Connect to parameters server
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #MechOS node to connect the mission commander to the mechos network
        self.mission_commander_node = mechos.Node("MISSION_COMMANDER", configs["ip"])

        #subscriber to listen if the movement mode is set to be autonomous mission mode
        self.movement_mode_subscriber = self.mission_commander_node.create_subscriber("MM", self._update_movement_mode_callback, configs["sub_port"])
        #subscriber to listen if the mission informatin has changed.
        self.update_mission_info_subscriber = self.mission_commander_node.create_subscriber("MS", self._update_mission_info_callback, configs["sub_port"])

        #subscriber to listen if the mission informatin has changed.
        self.update_mission_info_subscriber = self.mission_commander_node.create_subscriber("MS", self._update_mission_info_callback, configs["sub_port"])

        #subscriber to listen if object detection data is available
        self.neural_net_subscriber = self.mission_commander_node.create_subscriber("NN", self._update_neural_net_callback, configs["sub_port"])
        self.detection_data = [0.0, 0.0, 0.0, 0.0]
        self.neural_net_data = [0.0, 0.0, 0.0, 0.0]

        #Publisher to be able to kill the sub within the mission
        self.kill_sub_publisher = self.mission_commander_node.create_publisher("KS", configs["pub_port"])

        #Set up a thread to listen to request from the GUI
        self.command_listener_thread = threading.Thread(target=self._command_listener)
        self.command_listener_thread.daemon = True
        self.command_listener_thread_run = True
        self.command_listener_thread.start()

        self.neural_net_listener_thread = threading.Thread(target=self._neural_net_listener)
        self.neural_net_listener_thread.daemon = True
        self.neural_net_listener_thread_run = True
        self.neural_net_listener_thread.start()

        self.mission_tasks = [] #A list of the mission tasks
        self.mission_data = None #The .json file structure loaded into python dictionary

        self.run_thread = True
        self.daemon = True

        self.mission_mode = False #If true, then the subs navigation system is ready for missions
        self.mission_live = False  #Mission live corresponds to the autonomous buttons state.

        #Set up serial com to read the autonomous button
        com_port = self.param_serv.get_param("COM_Ports/auto")
        self.auto_serial = serial.Serial(com_port, 9600)

        #load the mission data
        self._update_mission_info_callback(None)

    def _update_movement_mode_callback(self, movement_mode):
        '''
        The callback function to select which navigation controller mode is being used.
        If it is set to 3, then the navigation controller is ready for autonomous mode.
        Parameters:
            movement_mode: Raw byte of the mode.
        Returns:
            N/A
        '''
        movement_mode = struct.unpack('b', movement_mode)[0]
        if(movement_mode == 3):
            print("[INFO]: Mission Commander Ready to Run Missions. Sub Initially Killed")

            #Initially have the sub killed when switched to mission commander mode
            kill_state = struct.pack('b', 1)
            self.kill_sub_publisher.publish(kill_state)

            self.mission_mode = True

        else:

            if(self.mission_mode == True):
                print("[INFO]: Exited Mission Command Mode.")

            self.mission_mode = False
            self.mission_live = False

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

        print("[INFO]: New Mission file set as %s", self.mission_file)
        #Parse the mission file
        self.parse_mission()

    def _update_neural_net_callback(self, neural_net_data):

        self.detection_data = struct.unpack('sfffffffffff', neural_net_data)
        #self.detection_data[0] = self.detection_data[0].decode("utf-8")
        print(self.detection_data)

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
                self.mission_commander_node.spinOnce(self.movement_mode_subscriber)

                if(self.auto_serial.in_waiting):
                    auto_pressed = (self.auto_serial.read(13)).decode()
                    self.auto_serial.read(2) #Read the excess two bytes

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
            time.sleep(0.2)

    def _neural_net_listener(self):
        while(self.neural_net_listener_thread):
            try:
                self.mission_commander_node.spinOnce(self.neural_net_subscriber)
            except Exception as e:
                print("[ERROR]: Neural net data not available. Error:", e)
            #time.sleep(0.2)


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
        print("[INFO]: Parsing Mission. Number of tasks for mission is", self.num_tasks, ".")

        task_keys = self.mission_data.keys()

        for task_index, task in enumerate(task_keys):

            #Get the task type and name
            task_type = self.mission_data[task]["type"]

            #generate waypoint task
            if(task_type == "Waypoint"):
                waypoint_task = Waypoint_Task(self.mission_data[task], self.drive_functions)
                self.mission_tasks.append(waypoint_task)

            #Generate Gate with no vision task
            elif(task_type == "Gate_No_Vision"):
                gate_no_vision = Gate_No_Vision_Task(self.mission_data[task], self.drive_functions)
                self.mission_tasks.append(gate_no_vision)

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
                    #print("[INFO]: Starting Mission")
                    #When mission is live, run the mission

                    unkill_state = struct.pack('b', 0)
                    self.kill_sub_publisher.publish(unkill_state)

                    #Set the current position as origin
                    self.sensor_driver.zero_pos()

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
                    kill_state = struct.pack('b', 1)
                    self.kill_sub_publisher.publish(kill_state)
            except:
                print("[ERROR]: Encountered an Error in Mission Commander. Error:", sys.exc_info()[0])
                raise



if __name__ == "__main__":

    mission_commander = Mission_Commander('MissionFiles/GateQual/mission.json', None)
