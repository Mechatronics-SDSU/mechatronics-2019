'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/30/2019

Description: This module contains the "Thruster" class which allows control of thruster
            speeds using PWM.
'''
import sys
import os

PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

import numpy as np
from MechOS import mechos
import serial
import time
import struct
from protoFactory import packageProtobuf
import Mechatronics_pb2
import copy

class Thruster():
    '''
    This class defines an object for individual thrusters. It let's you set the speed (and direction)
    of the thrusters. Setting the PWM signal will actually send the comman to the thruster.
    '''

    def __init__(self, maestro_serial_obj, thruster_id, orientation, location, max_thrust):
        '''
        Initialize settings for individual thruster.

        Parameters:
            maestro_serial_obj: The open serial communication port object connected
                                to the maestro motor controller.
            thruster_id: An int id value assigned to individual thrusters. Most
                        AUV's have thrusters assigned 1 - 8.
            orientation: A 3 element long list specifying the direction in which the
                        thruster controls. Typically thrusters control thruster in either
                        x, y, or z direction. Hence the list is in the form of
                        [x, y, z]. For example, if the given thruster controls the x direction,
                        its orientation should be [1, 0, 0].
            location: The physical location of the thruste with respect to the center of the
                        sub (as unit vectors). The center of the sub is considered the origin.
                        Again the list form is [x, y, z]. 'x' correspondes to the axis running
                        from the front to the back of the sub. 'y' corresponds to the axis
                        running left to right side of the sub. And 'z' corresponds to the
                        axis running from the bottom to the top of the sub.
            max_thrust: A value between 0 and 100 signifying the maximum thrust possible. Example,
                        80 would mean limiting the thruster to 80% it's maximum possible thrust at
                        all times
        '''
        self.maestro_serial_obj = maestro_serial_obj
        self.thruster_id = thruster_id
        self.orientation = orientation
        self.location = location
        self.max_thrust = max_thrust

        #remember the previous thrust value set in so you do not keep sending the same thrust value
        self.previous_thrust= None

    def set_thrust(self, thrust):
        '''
        Set the thrust value of the thruster and it to the maestro to drive the thruster.
        The thruster values will be bounded by the maximum thrust value.

        Parameters:
            thrust: At thrust value in the range of [-100, 100]. Where -100 is maximum reverse
            thrust and 100 is maximum normal direction thrust.

        Returns:
            N/A
        '''
        if thrust != self.previous_thrust:

            if thrust > self.max_thrust:
                self.previous_thrust = copy.copy(self.max_thrust)


                #Re-bound thrust from [-100, 100] to [0, 255] for writing PWM signal
                thrust = int(np.interp(self.max_thrust, [-100, 100], [0, 254]))

            elif thrust < (-self.max_thrust):

                self.previous_thurst = copy.copy(-self.max_thrust)

                thrust = int(np.interp(-self.max_thrust, [-100, 100], [0, 254]))

            else:
                self.previous_thrust = thrust

                thrust = int(np.interp(thrust, [-100, 100], [0, 254]))

            #write thrust to maestro
            self.maestro_serial_obj.write(bytearray([0xFF, self.thruster_id, thrust]))

class Thruster_Controller:
    '''
    This is a controller that will receive thrust values through a MechOS subscriber
    and write the values to the thrusters.
    '''
    def __init__(self, maestro_serial_obj, max_thrust):
        '''
        Intialize the thruster controller and communication to the MechOS network
        to receive thrust values.

        Parameters:
            maestro_serial_obj: The open serial communication port object connected
                                to the maestro motor controller.
            max_thrust: A value between 0 and 100 signifying the maximum thrust possible. Example,
                        80 would mean limiting the thruster to 80% it's maximum possible thrust at
                        all times
        '''
        #Type of proto to receive thruster values through
        self.type = "THRUSTERS"

        #Subscribe to the thrust publisher to receive thrust values
        self.thruster_control_node = mechos.Node("THRUSTER_CONTROL")
        self.subscriber = self.thruster_control_node.create_subscriber("THRUST", self._update_thrust)

        self.thrusters = []
        self.thrust_proto = Mechatronics_pb2.Mechatronics()

        #Declare objects for each thruster
        for thruster_id in range(8):
            self.thrusters.append(Thruster(maestro_serial_obj, thruster_id + 1, None,
                                None, max_thrust))

    def _update_thrust(self, thrust_proto_data):
        '''
        Call back function for the subscriber to pass the proto messages received.
        Parse the proto message and set the apprioriate thruster values.

        Parameters:
            thruster_proto_data: A proto buff message containging data under type
                                thruster.
        Returns:
            N/A
        '''
        self.thrust_proto.ParseFromString(thrust_proto_data)


        #Set all the thrusters
        self.thrusters[0].set_thrust(self.thrust_proto.thruster.thruster_1)
        self.thrusters[1].set_thrust(self.thrust_proto.thruster.thruster_2)
        self.thrusters[2].set_thrust(self.thrust_proto.thruster.thruster_3)
        self.thrusters[3].set_thrust(self.thrust_proto.thruster.thruster_4)
        self.thrusters[4].set_thrust(self.thrust_proto.thruster.thruster_5)
        self.thrusters[5].set_thrust(self.thrust_proto.thruster.thruster_6)
        self.thrusters[6].set_thrust(self.thrust_proto.thruster.thruster_7)
        self.thrusters[7].set_thrust(self.thrust_proto.thruster.thruster_8)


    def run(self):
        '''
        Continually listen for messages from a publisher giving thrust messages.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while(True):
            self.thruster_control_node.spinOnce(self.subscriber)
            time.sleep(0.1)

if __name__ == "__main__":
    maestro_serial_obj = serial.Serial('COM29', 9600)
    thruster_controller = Thruster_Controller(maestro_serial_obj, 80)
    thruster_controller.run()
