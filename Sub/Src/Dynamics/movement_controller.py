'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/08/2019
Description: This module contains a highest level movement controller for Perseverance.
                It contains multiple modes of control for the sub including
                thruster test mode, PID test mode, manual control mode PID,
                autonomous mode PID, LQR test mode, manual control mode LQR, and
                autonomous mode LQR.
'''
import sys
import os
import time

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
from protoFactory import packageProtobuf
import Mechatronics_pb2

from movement_pid import Movement_PID
from MechOS import mechos

class Movement_Controller:
    '''
    '''
    def __init__(self):
        '''
        '''

        #Initialize parameter server client
        self.param_serv = mechos.Parameter_Server_Client()
        parameter_xml_database = os.path.join("..", "Params", "Perseverance.xml")
        self.param_serv.use_parameter_database(parameter_xml_database)

        #Initialize the mechos node
        self.movement_controller_node = mechos.Node("MOVEMENT_CONTROLLER")

        #Setup mechos subscribers and proto decoders
        self.thruster_test_proto = Mechatronics_pb2.Mechatronics()
        self.thruster_test_sub = self.movement_controller_node.create_subscriber("THRUST",
                                                        self.thruster_test)

        #PID based movement controller
        self.movement_pid_controller = Movement_PID()

    def thruster_test(self, thrust_proto_data):
        '''
        '''
        self.thruster_test_proto.ParseFromString(thrust_proto_data)
        thrusts = [self.thruster_test_proto.thruster.thruster_1,
                   self.thruster_test_proto.thruster.thruster_2,
                   self.thruster_test_proto.thruster.thruster_3,
                   self.thruster_test_proto.thruster.thruster_4,
                   self.thruster_test_proto.thruster.thruster_5,
                   self.thruster_test_proto.thruster.thruster_6,
                   self.thruster_test_proto.thruster.thruster_7,
                   self.thruster_test_proto.thruster.thruster_8]
        print(thrusts)

        self.movement_pid_controller.simple_thrust(thrusts)


    def run(self):
        '''
        '''
        while(True):
            self.movement_controller_node.spinOnce(self.thruster_test_sub)
            time.sleep(0.01)
        pass

if __name__ == "__main__":
    movement_controller = Movement_Controller()
    movement_controller.run()
