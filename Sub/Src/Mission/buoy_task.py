import sys
import os
import time

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

import csv
import numpy as np
from task import Task

class Buoy_Task(Task):

    '''
    Use neural network data to detect and hit buoys after judging their pose with
    respect to the sub
    '''

    def __init__(self, task_dict, drive_functions, mission_commander_obj):

        '''
        Initialize the buoy task given the task dictionary
        Parameters:
            task_dict: A python dictionary containing parameters for the buoy task
                      {
                        "type": "Buoy"
                        "name": <task_name>
                        "timeout": <timeout_time_minutes>
                        "line_up_position: <The yaw,north,east,depth position to start detections"
                        "stabilization_time: <The time(sec) to wait for stabilization at line_up_position>"
                        "move_forward_dist: <The number of feet move forward in the x direction of the sub"
                        }

            drive_functions: An already initialized object of drive functions. This
                    class contains a variety of drive functions that are useful to complete
                    tasks.

            neural_net_data: A list containing the neural network data for our detected buoys.
                This list has the label, the confidence interval, the coordinates for the detection,
                and the rotation and translation vectors of the object from the camera
        '''

        Task.__init__(self)

        self.name = self.task_dict["name"]
        self.type = "Buoy"
        self.timeout = self.task_dict["timeout"] #timeout for the entire task
        self.detection_timeout = self.task_dict["detection_timeoutFse"] #time out at the observervation point

        self.timeout_timer = util_timer.Timer()
        self.detection_timeout_timer = util_timer.Timer()

        self.observation_position = self.task_dict["observation_position"]
        self.position_buffer_zone = self.task_dict["position_buffer_zone"]
        self.depth_buffer_zone = self.task_dict["depth_buffer_zone"]
        self.yaw_buffer_zone = self.task_dict["yaw_buffer_zone"]

        #The name of the object and confidence detection
        self.object_type = self.task_dict["object_type"]
        self.object_confidence = self.task_dict["object_confidence"]

        self.drive_functions = drive_functions

        self.mission_commander = mission_commander_obj

        self.calculated_depth = 0.0
        self.calculated_yaw = 0.0
        self.calculated_y = 0.0
        self.calculated_x = 0.0

        #This is a buffer of the detections for the object type we are looking for
        #if there are ten object detection, stop collecting in the buffer
        self.object_detections_buffer = []
        #TODO: Add more mission params later

    def go_to_observation_position(self):
        '''
        Function to go to the observation position.

        Parameters:
            N/A
        Returns:
            True: If no timeout occurred.
            False: If a timeout occurred.
        '''

        #Dive to depth of the desired_line_up_position
        desired_yaw, desired_north, desired_east, desired_depth = self.observation_position
        print("Desired_Yaw,", desired_yaw)

        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_to_depth(desired_depth=desired_depth,
                                                            buffer_zone=self.depth_buffer_zone,
                                                            timeout=remaining_task_time)
        if(not succeeded):
            return False
        #Face the desired_line_up_position
        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, ret_yaw = self.drive_functions.move_to_face_position(north_position=desired_north,
                                                        east_position=desired_east,
                                                        buffer_zone=self.yaw_buffer_zone,
                                                        timeout=remaining_task_time,
                                                desired_orientation={"depth":desired_depth})

        if(not succeeded):
            return False
        #Drive to the desired_line_up_position
        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _, _ = self.drive_functions.move_to_position_hold_orientation(north_position=desired_north,
                                                                      east_position=desired_east,
                                                                      buffer_zone=self.position_buffer_zone,
                                                                      timeout=remaining_task_time,
                                                            desired_orientation={"depth":desired_depth, "yaw":ret_yaw})

        if(not succeeded):
            return False

        #Face the correct yaw for the line_up_position

        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_to_yaw(desired_yaw=desired_yaw,
                                                        buffer_zone=self.yaw_buffer_zone,
                                                        timeout=remaining_task_time,
                                                        desired_orientation={"depth":desired_depth,
                                                                            "north_pos":desired_north,
                                                                            "east_pos":desired_east})
        return True

    def collect_detections(self):
        '''
        Sit at desired detection spot until enough detection data has been gathered. When
        enough has been gathered, we will run an average
        '''
        if(len(self.object_detections_buffer) >= 10):
            return True

        elif(len(self.mission_commander.neural_net_data) > 0):
            object_detection_data = self.mission_commander.neural_net_data.pop(0)

            #if it is the object we are looking for.
            if(self.object_type == object_detection_data[0] and object_detection_data[1] >= self.object_confidence):

                self.object_detections_buffer.append(object_detection_data)

            return False
        else:
            return False

    def hit_buoy(self):
        '''
        Calculate the pose of the object with respect to the sub's camera. Adjust the sub
        according to how the dice or buoy is oriented. We want it to achieve desired depth
        first, then yaw, then move y direction, then move x
        '''

        pass

    def run(self):
        '''
         Run the hit object task. This task will have the sub go to the observe position
         where it will attempt to look for the desired object having self.object_type with
         a detected object confidence of self.object_confidence. If the sub detects the object
         at least N times, then the sub will calculate the position it should drive to hit it.
        '''

        #Go to observe position
        succeeded = self.go_to_observation_position()

        if( not succeeded):
            return False

        #Clear the all the neural network data in the neural net queue
        self.mission_commander.neural_net_data.clear()

        #Start the observation timer to get detection and look for detections
        while(((self.detection_timeout - self.detection_timeout_timer.net_timer()) > 0) and \
                ((self.timeout - self.timeout_timer.net_timer()) > 0)):

            #Attemp to collect detections
            enough_detections_found = self.collect_detections()

            if(enough_detections_found):
                break

        if not enought_detection_found:
            return False

        #Take the average of the detections
        sub_x_direction, sub_y_direction, sub_depth_direction = 0, 0, 0
        for i in range(10):

            sub_x_direction += self.object_detections_buffer[i][11]
            sub_y_direction += self.object_detections_buffer[i][9]
            sub_depth_direction += self.object_detections_buffer[i][10]

        sub_x_direction /= 10.0
        sub_y_direction /= 10.0
        sub_depth_direction /= 10.0

        #Move to the depth
        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_to_depth(desired_depth=sub_depth_direction,
                                                            buffer_zone=self.depth_buffer_zone,
                                                            timeout=remaining_task_time,
                                                            desired_orientation={"yaw":self.observation_position[0]})
        if(not succeeded):
            return False
        #Face the desired_line_up_position
        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _, _ = self.drive_functions.move_y_direction(sub_y_direction,
                                                        buffer_zone=self.yaw_buffer_zone,
                                                        timeout=remaining_task_time,
                                                desired_orientation={"depth":(self.observation_position[3] + sub_depth_direction), "yaw":self.observation_position[0]})

        if(not succeeded):
            return False

        #Face the desired_line_up_position
        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _, _ = self.drive_functions.move_x_direction(sub_x_direction,
                                                        buffer_zone=self.yaw_buffer_zone,
                                                        timeout=remaining_task_time,
                                                desired_orientation={"depth":(self.observation_position[3] + sub_depth_direction), "yaw":self.observation_position[0], "east_pos":(self.observation_position[2] + sub_y_direction)})
