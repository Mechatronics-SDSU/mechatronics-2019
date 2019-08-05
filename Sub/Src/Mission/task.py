'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 07/19/2019
Description: This file has the Parent Task class that all tasks should inherit
             from. It contains controls such as task name, task timer, etc.
'''
import sys
import os

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

import time

class Task:
    '''
    The Task class contains basic attributes and functions of task that are executed
    in a mission. Essentially it outlines the structure of how a task should be
    built.
    '''
    def __init__(self):
        '''
        Basic outline initialization of a task.

        Parameters:
            timeout: How long the task has before it is exited.

        Returns:
            N/A
        '''

        #Dictionary containing all of the task information.
        self.task_dict = None

        #Provide a name for your task
        self.name = None

        #Provide a type for your task. This type will be used by the Mission Commander
        #to part
        self.type = None
        self.timeout = None
        self.timeout_timer = util_timer.Timer()

    def print_task_info(self):
        '''
        Print basic information about the task.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        print("[INFO]:Task Name:", self.name)
        print("\tTask Type:", self.type)
        print("\tTimeout Time for Task: %0.2f min" % timeout)

    def run(self):
        '''
        Run the task. This is the function that the running execution parts of your
        task should be coded.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        pass
