'''
Copyright 2019, Mohammad Shafi, All rights reserved
Author: Mohammad Shafi <ma.shafi99@gmail.com>
Last modified: 06/24/2019
Description: This module sends Xbox inputs over socket to the movement
             controller
'''

import pygame
import socket
import struct
import numpy as np
import time
from MechOS.message_passing.Nodes.node_base import node_base

class remote_control_node(node_base):
    '''
    This class will listen to Xbox inputs, and only four values: Left stick
    horizontal movement for x, left stick vertical for y, right stick horizontal
    for yaw, and either the left or right trigger for depth
    '''

    def __init__(self, IP, MEM):
        '''
        Initialize the input axes and the node, prepare for message sending

        Parameters:
            IP: dictionary which holds all the necessary components for network
                transfer, including IP address, sockets, etc
            MEM: dictionary used for local message transfer

        Returns:
            N/A
        '''
        node_base.__init__(self, MEM, IP)

        #Disgusting pygame stuff
        pygame.init()
        pygame.joystick.init()
        self._joystick = pygame.joystick.Joystick(0)
        self._joystick.init()

        self._axes = [0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0]
        self._memory = MEM
        self._ip_route = IP
        self._remote_depth_hold = False
        self._record_waypoint = False
        self._zero_waypoint = False

    def _control(self, axis_array):
        '''
        Check the state of all axes during every axis motion. This allows us
        to control multiple thrusters simultaneously

        Parameters:
            axis_array: Array of axes to map
            input: The actual pygame event

        Returns:
            Array of desired values after modifications are made, packed as
            bytes
        '''
        depth = 0.0

        #Set deadzones, these triggers too sensitive. Strafe
        if axis_array[0] > -0.3 and axis_array[0] < 0.3:
            axis_array[0] = 0.0

        #FW/BWD
        if axis_array[1] > -0.3 and axis_array[1] < 0.3:
            axis_array[1] = 0.0

        #Yaw
        if axis_array[3] > -0.3 and axis_array[3] < 0.3:
            axis_array[3] = 0.0

        #Depth

        if axis_array[2] > 0:
            depth = -1 * ((axis_array[2] + 1)/2)
        elif axis_array[4] > 0:
            depth = (axis_array[4] + 1)/2

        byte_axis_array = struct.pack('ffff???',
                                            axis_array[3],
                                            axis_array[1],
                                            axis_array[0],
                                            depth,
                                            axis_array[5],
                                            axis_array[6],
                                            axis_array[7])

        return byte_axis_array

    def run(self):
        '''
        Continuously send the Xbox data as bytes via udp over the network
        specified

        Parameters:
            N/A

        Returns:
            N/A
        '''

        while True:

            #Set the axes for every event. This gives us simultaenous control
            #over multiple thrusters
            if pygame.event.peek():

                instance = pygame.event.poll()

                self._axes[0] = self._joystick.get_axis(0)
                self._axes[1] = self._joystick.get_axis(1)

                #map triggers differently, cuz default state is not 0
                self._axes[2] = self._joystick.get_axis(2)
                self._axes[3] = self._joystick.get_axis(3)

                #map triggers differently, cuz default state is not 0
                self._axes[4] = self._joystick.get_axis(5)

                if instance.type == pygame.JOYBUTTONUP:
                    if instance.button == 1:
                        self._remote_depth_hold = not self._remote_depth_hold
                    if instance.button == 0:
                        self._record_waypoint = True
                    if instance.button == 2:
                        self._zero_waypoint = True

                self._axes[5] = self._remote_depth_hold
                self._axes[6] = self._record_waypoint
                self._axes[7] = self._zero_waypoint
                self._send(msg=(self._control(self._axes)), register = 'RC', local = False, foreign = True)
                self._record_waypoint = False
                self._zero_waypoint = False

            else:
                #print(self.remote_depth_hold)
                time.sleep(0)

if __name__ == '__main__':

    rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('192.168.1.14', 6312)

    IP={'RC':
            {
            'address': ip_address,
            'sockets': (rc_socket, thrust_socket),
            'type': 'UDP'
            }
        }
    MEM={'RC':b'cleaners'}
    remote_node = remote_control_node(IP, MEM)
    remote_node.start()
