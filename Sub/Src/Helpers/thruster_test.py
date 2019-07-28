'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 06/11/2019

Description: Send thruster values to all 8 thrusters.
'''
import sys
import os

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

MESSAGE_TYPE_PATH = os.path.join("..","..", "..", "Message_Types")
sys.path.append(MESSAGE_TYPE_PATH)
from thruster_message import Thruster_Message

import numpy as np
from MechOS import mechos

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--thrust", type=int, nargs=8,
            help="Input the thrust percentage you want to test at. Range [-100, 100]",
            required=True)

    args = parser.parse_args()
    print(args.thrust)

    configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

    #MechOS publisher to send thrust test messages to thruster controller
    thruster_test_node = mechos.Node("THRUSTER_TEST_HELPER", '192.168.1.2', '192.168.1.14')
    publisher = thruster_test_node.create_publisher("THRUSTS", Thruster_Message(), protocol="tcp")

    publisher.publish(args.thrust)
