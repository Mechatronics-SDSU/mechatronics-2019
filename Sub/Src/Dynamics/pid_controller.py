'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/05/2019
Description: This module contains a PID controller class that is
            used for feedback control systems.
'''

import sys
import os

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

import time


class PID_Controller():
    '''
    PID controller typically used in control feed back systems.
    '''
    def __init__(self, k_p, k_i, k_d, d_t, l_bound=None, u_bound=None):
        '''
        Initialize the the PID controller parameters.

        Parameters:
            k_p: Proportional gain
            k_i: Integral gain
            k_d: Derivative gain
            d_t: Time interval between calculating to output control
            l_bound: Lower bound for PID output
            u_bound: Upper bound for PID output
        Returns:
            N/A
        '''
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.d_t = d_t
        self.l_bound = l_bound
        self.u_bound = u_bound

        self.integral = 0
        self.previous_error = 0

        #Timer to check difference time in between control calculations
        self.PID_timer = util_timer.Timer()


    def set_gains(self, k_p, k_i, k_d, d_t=None):
        '''
        Reset the gain parameters.

        Parameters:
            k_p: Proportional gain
            k_i: Integral gain
            k_d: Derivative gain
            d_t: Time interval between calculating to output control.
                    If no value is passed, it will stay what it originally
                    was set to during initialization.
        '''
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.d_t = d_t
    def control_step(self, error):
        '''
        Perfrom a control step to correct for error in control system.

        Parameters:
            error: The error from current point to desired set point.

        Returns:
            PID: An PID output control value to correct for error in system
        '''
        P = self.k_p * error #proportional term

        #Ensure semi time difference in between each control step
        calc_time_interval = self.PID_timer.net_timer()
        if( calc_time_interval < self.d_t):
            time.sleep((self.d_t - calc_time_interval))
            self.PID_timer.restart_timer()

        self.integral = self.integral + (error * self.d_t)
        I = self.k_i * self.integral

        D = self.k_d * (error - self.previous_error) / self.d_t

        PID = P + I + D

        if(self.l_bound != None):
            if(PID < self.l_bound):
                PID = self.l_bound
        if(self.u_bound != None):
            if(PID > self.u_bound):
                PID = self.u_bound

        return PID
