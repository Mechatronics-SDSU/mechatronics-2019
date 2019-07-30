'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
        Chrisitian Gould<christian.d.gould@gmail.com>
        Alexa Becerra<alexa.becerra99@gmail.com>
Last Modified 07/29/2019
Description: This module is a simple task for doing an initial dive.
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

class Initial_Dive_Task(Task):
    '''
    When the sub is diving from the surface, this task will ramp up the
    thrusts to make the initial dive smoother.
    '''
    def __init__(self, task_dict, drive_functions):
        '''
        Initialize the Dive task given the task dictionary.

        Parameters:
            task_dict: A python dictionary containing the data about ramping
                        to a specific dive
        '''
        Task.__init__(self)

        self.task_dict = task_dict

        self.name = self.task_dict["name"]
        self.type = "Initial_Dive"

        self.drive_functions = drive_functions

    def run(self):
        '''
        Run the initial dive task by using an exponential over time to
        change the desired depth.

        Parameters:
            N/A

        Returns:
            True
        '''
        print("[INFO]: Starting Initial Dive.")

        set_dive_depth = 3.0
        start_time = time.time()
        constant_offset = time.sleep
        offsets = np.arange(0,3.3,.3)

        offset_depths = 3**((offsets)/3)
        for depth in offset_depths:
            #Send depth
            self.driver_functions.move_to_depth(depth, buffer_zone=0.01, timeout=0.0, )
            constant_offset(.5)
