'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 07/3/2019
Description: This module defines a basic gate mission that strictly uses waypoints
            and no vision for detection of the gate. It also allows to perform a trick
            where the sub will go backwards through the gate.
'''
import sys
import os
import time

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer
import csv
import numpy as np

from task import Task

class Gate_No_Vision_Task(Task):
    '''
    Drive through the gate using strictly waypoints. If the task cannot be completed
    in time, then the task will fail.
    '''
    def __init__(self, task_dict,drive_functions):
        '''
        Initialize the Gate task give the task description dictionary.

        Parameters:
            task_dict: A python dictionary containing the parameters for
                    the waypoint task.
                    Dictionary Form:
                    ---------------------------
                    {
                        "type": "Gate_No_Visision"
                        "name": <task_name>
                        "timeout": <timeout_time_minutes>
                        "line_up_position":<the Yaw/North/East/Depth position to line up too infront of the gate>
                        "stabilization_time": <The time (sec) to wait for stabilization at line_up_position>
                        "move_forward_dist": <The number of feet to move forward in the x direction of the sub to drive through the gate>
                    }
            drive_functions: An already initialized object of drive functions. This
                    class contains a variety of drive functions that are useful to complete
                    tasks.
        '''

        Task.__init__(self)

        self.task_dict = task_dict

        #Unpack the information about the task
        self.name = self.task_dict["name"]
        self.type = "Gate_No_Vision"
        self.timeout = self.task_dict["timeout"] * 60.0 #In Seconds now.

        #Timer to be used to keep track of how long the task has been going.
        self.timeout_timer = util.Timer()

        self.line_up_position = self.task_dict["line_up_position"]
        self.position_buffer_zone = self.task_dict["position_buffer_zone"]
        self.depth_buffer_zone = self.task_dict["depth_buffer_zone"]
        self.yaw_buffer_zone = self.task_dict["yaw_buffer_zone"]
        self.stablization_time = self.task_dict["stabilization_time"]
        self.move_forward_dist = self.task_dict["move_forward_dist"]

        #If true, then the sub will attempt to go through the gate backwards
        self.go_through_gate_backwards = self.task_dict["go_through_gate_backwards"]
        if(self.go_through_gate_backwards):
            self.move_forward_dist *= -1 #Reverse the direction to go forward to go backwards

            desired_yaw = self.line_up_position[0] + 180 #Flip the yaw 180 deg to go backwards
            if(desired_yaw > 360):
                self.line_up_position[0] = 360 - desired_yaw

    def print_task_info(self):
        '''
        Print the task information

        Parameters:
            N/A
        Returns:
            N/A
        '''
        print("[INFO]: Task Name:", self.name)
        print("\tTask Type:", self.type)
        print("\tTimeout Time: %0.2f min" % self.timeout / 60.0)
        print("\tLine up Position for Gate: Yaw=%0.2fft, North=%0.2fft, East=%0.2fft, Depth=%0.2fft" % tuple(self.line_up_position))
        print("\tGo Through Gate Backwards:", bool(self.go_through_gate_backwards))

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
        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        succeeded, _ = self.drive_functions.move_to_depth(desired_depth=depth_position,
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
                                                                            "north":desired_north,
                                                                            "east":desired_east})
        return True

    def run(self):
        '''
        Run the gate task without using any vision (use only waypoints). If a timeout
        occurs, exit the task with a failure.

        Parameters:
            N/A
        Returns:
            True: If the gate task was complete within the timeout
            False: If the task reaches a timout.
        '''
        print("[INFO]: Starting Gate with No Visison Task:", self.name)
        self.print_task_info()

        self.timeout_timer.restart_timer()

        #Go to the lineup position
        succeeded = self.go_to_line_up_position()

        if(not succeeded):
            return False

        time.sleep(self.stabilization_time)

        remaining_task_time = self.timeout - self.timeout_timer.net_timer()
        self.drive_functions.move_x_direction(distance_x=self.move_forward_dist,
                                                buffer_zone=self.position_buffer_zone,
                                                timeout=remaining_task_time)

        if(not succeeded):
            return False

        return True #Task complete.
