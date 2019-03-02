'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/30/2019

Description: Send a short pulse to a single thruster for testing.
'''
import sys
import os

THRUSTER_LIB_PATH = os.path.join("..", "Dynamics")
sys.path.append(THRUSTER_LIB_PATH)
from thruster import Thruster

import serial
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--thruster_id", type=int,
                    help="Input the thruster number desired to be tested", required=True)
    parser.add_argument("--thrust", type=int,
            help="Input the thrust percentage you want to test at. Range [-100, 100]",
            required=True)

    args = parser.parse_args()

    maestro_serial_obj = serial.Serial('COM29', 9600)

    #Limit the test thrust to 50% thrust capacity
    test_thruster = Thruster(maestro_serial_obj, args.thruster_id, None, None, 50)
    test_thruster.set_thrust(args.thrust)
