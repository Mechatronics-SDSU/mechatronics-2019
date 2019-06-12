'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 06/11/2019

Description: Send thruster values to all 8 thrusters.
'''
import sys
import os

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import thrusters_pb2

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

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
    thruster_test_node = mechos.Node("THRUSTER_TEST", configs["ip"])
    publisher = thruster_test_node.create_publisher("TT", configs["pub_port"])

    #Initialize the thruster test proto to package thrust requests
    thruster_test_proto = thrusters_pb2.Thrusters()
    thruster_test_proto.thruster_1 = args.thrust[0]

    thruster_test_proto.thruster_2 = args.thrust[1]
    thruster_test_proto.thruster_3 = args.thrust[2]
    thruster_test_proto.thruster_4 = args.thrust[3]
    thruster_test_proto.thruster_5 = args.thrust[4]
    thruster_test_proto.thruster_6 = args.thrust[5]
    thruster_test_proto.thruster_7 = args.thrust[6]
    thruster_test_proto.thruster_8 = args.thrust[7]

    print(thruster_test_proto)
    serialized_thruster_data = thruster_test_proto.SerializeToString()
    ##publish data to mechos network
    publisher.publish(serialized_thruster_data)
