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

    def __init__(self, task_dict, drive_functions, neural_net_data):

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
        self.line_up_timeout = self.task_dict["line_up_timeout"]
        self.detection_timeout = self.task_dict["detection_timeoutFse"]

        self.line_up_timeout_timer = util_timer.Timer()
        self.detection_timeout_timer = util_timer.Timer()

        self.line_up_position = self.task_dict["line_up_position"]
        self.position_buffer_zone = self.task_dict["position_buffer_zone"]
        self.depth_buffer_zone = self.task_dict["depth_buffer_zone"]
        self.yaw_buffer_zone = self.task_dict["yaw_buffer_zone"]
        self.stabilization = self.task_dict["stabilization_time"]
        self.move_forward_dist = self.task_dict["move_forward_dist"]

        self.drive_functions = drive_functions

        self.neural_net_data = neural_net_data
        self.calculated_depth = 0.0
        self.calculated_yaw = 0.0
        self.calculated_y = 0.0
        self.calculated_x = 0.0


        #TODO: Add more mission params later

    def go_to_line_up_position(self):
        '''
        Function to go to the line up position.

        Parameters:
            N/A
        Returns:
            True: If no timeout occurred.
            False: If a timeout occurred.
        '''

        #Dive to depth of the desired_line_up_position
        desired_yaw, desired_north, desired_east, desired_depth = self.line_up_position
        print("Desired_Yaw,", desired_yaw)

        remaining_task_time = self.line_up_timeout - self.line_up_timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_to_depth(desired_depth=desired_depth,
                                                            buffer_zone=self.depth_buffer_zone,
                                                            timeout=remaining_task_time)
        if(not succeeded):
            return False
        #Face the desired_line_up_position
        remaining_task_time = self.line_up_timeout - self.line_up_timeout_timer.net_timer()
        succeeded, ret_yaw = self.drive_functions.move_to_face_position(north_position=desired_north,
                                                        east_position=desired_east,
                                                        buffer_zone=self.yaw_buffer_zone,
                                                        timeout=remaining_task_time,
                                                desired_orientation={"depth":desired_depth})

        if(not succeeded):
            return False
        #Drive to the desired_line_up_position
        remaining_task_time = self.line_up_timeout - self.line_up_timeout_timer.net_timer()
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
        depth_desired = 0
        yaw_desired = 0
        strafe_desired = 0
        forward_desired = 0

        for i in range(0, 10):
            depth_desired = depth_desired + self.neural_net_data[10]
            yaw_desired = 0.0
            strafe_desired = strafe_desired + self.neural_net_data[9]
            forward_desired = forward_desired + self.neural_net_data[11]

        self.calculated_depth = float(depth_desired/10.0)
        self.calculated_yaw = float(yaw_desired/10.0)
        self.calculated_y = float(strafe_desired/10.0)
        self.calculated_x = float(forward_desired/10.0)

    def hit_buoy(self):
        '''
        Calculate the pose of the object with respect to the sub's camera. Adjust the sub
        according to how the dice or buoy is oriented. We want it to achieve desired depth
        first, then yaw, then move y direction, then move x
        '''

        remaining_task_time = self.detection_timeout - self.detection_timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_to_depth(desired_depth=self.calculated_depth,
                                                            buffer_zone=self.depth_buffer_zone,
                                                            timeout=remaining_task_time)

        remaining_task_time = self.detection_timeout - self.detection_timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_y_direction(distance_y=self.calculated_y,
                                                             buffer_zone=self.)
