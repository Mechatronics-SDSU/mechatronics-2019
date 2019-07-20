'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 07/3/2019
Description: This module defines how to perform a waypoint task. It
            ingest's a dictionary containing all of the necessary parameters
            to perform a waypoint mission. This is passed in from the Mission
            Controller.
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

class Waypoint_Task(Task):
    '''
    Given the waypoint task description dictionary, drive along the waypointed
    route. If the the task cannot be completed within the given timeout time,
    exit the mission and considerate it a failure.
    '''
    def __init__(self, task_dict, drive_functions):
        '''
        Initialize the waypoint task given the waypoint dict.

        Parameters:
            task_dict: A python dictionary containing the parameters
                                for the waitpoint task.
                            Dictionary Form:
                            -------------------
                            {
                                "type": "Waypoint"
                                "name": <task_name>
                                "timeout": <timeout_time_minutes>
                                "position_buffer_zone": <buffer zone for each (North, East) position (ft)>
                                "depth_buffer_zone": <buffer zone for depth moves (ft)>
                                "yaw_buffer_zone": <buffer zone for yaw moves (deg)>
                                "waypoint_file": <location of csv file containing waypoints>
                            }
            drive_functions: An already initialized object of drive_functions. This
                            class contains a variety of drive functions that are useful
                            to complete tasks.
        '''

        Task.__init__(self)

        self.task_dict = task_dict

        #Unpack the information about the task
        self.name = self.task_dict["name"]
        self.type = "Waypoint"
        self.timeout = self.task_dict["timeout"] * 60.0
        self.waypoint_file = self.task_dict["waypoint_file"]

        #Buffer zone (bubble) for North/East positions to be considered in at correct coordinate
        self.position_buffer_zone = self.task_dict["position_buffer_zone"]

        #The buffer zone used to be considered to make it to a certain depth when doing a depth dive
        self.depth_buffer_zone = self.task_dict["depth_buffer_zone"]

        #The buffer zone to be used for yaw to consider making it to a certain yaw position
        self.yaw_buffer_zone = self.task_dict["yaw_buffer_zone"]


        self.drive_functions = drive_functions

        #Initialize the timeout timer
        self.timeout_timer = util_timer.Timer()

        self.unpack_waypoints()

    def print_task_info(self):
        '''
        Print the task information.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        print("[INFO]:Task Name:", self.name)
        print("\tTask Type:", self.type)
        print("\tLocation of Waypoint File:", self.waypoint_file)
        print("\tTimeout Time for Task: %0.2f min" % self.timeout / 60.0)
        print("\tBuffer Zone Distance for North/East Positions: %0.2fft" % self.position_buffer_zone)
        print("\tBuffer Zone Distance for Depth Positions: %0.2fft" % self.depth_buffer_zone)
        print("\tBuffer Zone Distance for Yaw Positions: %0.2fft" % self.yaw_buffer_zone)

    def unpack_waypoints(self):
        '''
        Unpack the waypoint from the waypoint file and save them to a numpy matrix

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.waypoints = None

        with open(self.task_dict["waypoint_file"]) as waypoint_file:
            csv_reader = csv.reader(waypoint_file, delimiter=',')

            for waypoint_id, waypoint in enumerate(csv_reader):

                waypoint = [float(point) for point in waypoint] #Convert the values from csv to floats (they are read initially as strings)

                #Initialize waypoints numpy array on the first iteration through reading the csv.
                if(waypoint_id == 0):
                    self.waypoints = np.array(waypoint).reshape(1, 4)
                else:
                    self.waypoints = np.append(self.waypoints, np.array(waypoint).reshape(1, 4), axis=0) #append waypoints as rows

        waypoint_file.close()

    def run(self):
        '''
        Run through each of the waypoints. If a timout occurs, exit the mission with a
        failure.

        Parameters:
            N/A
        Returns:
            True: If the waypoint task was completed in its entirety without timing
                    out.
            False: If the waypoint task reaches its timeout but hasn't finished.
        '''
        print("[INFO]: Starting Waypoint Task:", self.name)

        self.print_task_info()

        self.timeout_timer.restart_timer()

        task_time = self.timeout

        #Iterate through each waypoint. Only move onto the next waypoint after
        #you have made it the current one

        for waypoint_id in range(0, self.waypoints.shape[0]):
            #The order from moving to waypoint to waypoint is
            #1st: Dive to the desired_depth
            #2nd: Turn yaw to face desired_position
            #3rd: Drive to the desired waypoint position
            north_position = self.waypoints[waypoint_id, 1]
            east_position = self.waypoints[waypoint_id, 2]
            depth_position = self.waypoints[waypoint_id, 3]
            #Dive to depth with allowable buffer zone of 0.1
            remaining_task_time = task_time - self.timeout_timer.net_timer()
            succeeded, _ = self.drive_functions.move_to_depth(desired_depth=depth_position,
                                                buffer_zone=self.depth_buffer_zone,
                                                timeout=remaining_task_time)
            if(not succeeded):
                return False

            #Face position desired_position while holding the previous desired depth.
            remaining_task_time = task_time - self.timeout_timer.net_timer()
            succeeded, desired_yaw = self.drive_functions.move_to_face_position(north_position=north_position,
                                                            east_position=east_position,
                                                            buffer_zone=self.yaw_buffer_zone,
                                                            timeout=remaining_task_time,
                                                    desired_orientation={"depth":depth_position})

            if(not succeeded):
                return False
            #Drive to the desired_position
            remaining_task_time = task_time - self.timeout_timer.net_timer()
            succedded, _, _ = self.drive_functions.move_to_position_hold_orientation(north_position=north_position,
                                                                          east_position=east_position,
                                                                          buffer_zone=self.position_buffer_zone,
                                                                          timeout=remaining_task_time,
                                                                desired_orientation={"depth":depth_position, "yaw":desired_yaw})
            if(not succeeded):
                return False

            print("[INFO]: Waypoint Task %s: North=%0.2f, East=%0.2f, Depth=%0.2f successfully reached." \
                                % (self.task_dict["name"], north_position, east_position, depth_position))
        return True
