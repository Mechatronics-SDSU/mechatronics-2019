'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 06/11/2019

Description: Send thruster values to all 8 thrusters.
'''
import sys
import os
import time

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

def set_thrust_proto(thruster_test_proto, thrusts):
    thruster_test_proto = thrusters_pb2.Thrusters()
    thruster_test_proto.thruster_1 = thrusts[0]
    thruster_test_proto.thruster_2 = thrusts[1]
    thruster_test_proto.thruster_3 = thrusts[2]
    thruster_test_proto.thruster_4 = thrusts[3]
    thruster_test_proto.thruster_5 = thrusts[4]
    thruster_test_proto.thruster_6 = thrusts[5]
    thruster_test_proto.thruster_7 = thrusts[6]
    thruster_test_proto.thruster_8 = thrusts[7]
    return(thruster_test_proto)


if __name__ == "__main__":


    configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()
    #MechOS publisher to send thrust test messages to thruster controller
    thruster_test_node = mechos.Node("THRUSTER_TEST", configs["ip"])
    publisher = thruster_test_node.create_publisher("TT", configs["pub_port"])

    #Initialize the thruster test proto to package thrust requests
    thruster_test_proto = thrusters_pb2.Thrusters()
    thruster_test_proto.thruster_1 = 0
    thruster_test_proto.thruster_2 = 0
    thruster_test_proto.thruster_3 = 0
    thruster_test_proto.thruster_4 = 0
    thruster_test_proto.thruster_5 = 0
    thruster_test_proto.thruster_6 = 0
    thruster_test_proto.thruster_7 = 0
    thruster_test_proto.thruster_8 = 0

    time.sleep(2)

    for i in range(8):
        thrusts = [0, 0, 0, 0, 0, 0, 0, 0]
        thrusts[i] = 10
        serialized_thruster_proto = (set_thrust_proto(thruster_test_proto, thrusts)).SerializeToString()
        publisher.publish(serialized_thruster_proto)
        time.sleep(2)
    
    serialized_thruster_data = (set_thrust_proto(thruster_test_proto, [0,0,0,0,0,0,0,0])).SerializeToString()
    
    #publish data to mechos network
    publisher.publish(serialized_thruster_data)

