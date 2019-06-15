'''
Copyright 2019, Mohammad Shafi, All rights reserved
Author: Mohammad Shafi <ma.shafi99@gmail.com>
Description: Successfully maps Xbox inputs to thrusters, whether on the sub
or on the servo testbench
'''

import pygame
import numpy as np
from message_passing.Nodes.node_base_udp import node_base
import message_passing

class RemoteControlNode(node_base):

    def __init__(self, IP, MEM):
        '''
        This class initializes the Xbox remote control and handles all input logic.
        It inherits functionality from node_base. The idea is to accept input from the
        Xbox control, map it into a thruster matrix, and then send that matrix over the
        network via udp to the address specified by the user.

        Parameters:
            IP:A dictionary containing the address and sockets to connect to for
               publish and subscribes
            MEM:Also a dictionary, contains local keys to update. Used for local
                data transfer

        Returns: N/A
        '''

        node_base.__init__(self, MEM, IP)
        pygame.init()   #Disgusting pygame stuff
        pygame.joystick.init()
        self._joystick = pygame.joystick.Joystick(0)
        self._joystick.init()

        self._memory = MEM  #Standard getters/setters for network and local
        self._ip_route = IP
        self._matrix = [0.0, 0.0, 0.0, 0.0]

        self.dot_product_matrix = np.array([[0, 0, 0, 0, 0, 0, 0, 1],
                                            [0, 0, 0, 1, 0, 0, 0, 0],
                                            [0, 0, 0, 1, 0, 0, 0, 1],
                                            [1, 0, 1, 0, 1, 0, 1, 0],
                                            [1, 0, 1, 0, 1, 0, 1, 0]])

    def _dot_product(self, input_matrix):
        '''
        Dots the Xbox input matrix with the control logic map we want for thrusters.
        Left stick controls yaw and x (forward) movement. Triggers control submerge
        and breach (depth). Right stick works as a multiplier to slowly kill thruster power
        in order to pitch and roll
        Parameters:
            input_matrix:The matrix of Xbox input values we use to multiply by the logic map
                         to write to the thrusters
        Returns:
            An output matrix which we send to the thruster node. Contains power values for thrusters
        '''

        return np.dot(input_matrix, self._dot_product_matrix)

    def _control(self, input):
        '''
        Takes the Xbox input from pygame's queue, and creates an input matrix with it
        This input matrix gets dotted with the dot product to give us the correct values
        to write to the thrusters
        '''
        if input.type == pygame.JOYAXISMOTION:
            if input.axis == 0:    #Left-stick, horizontal, controls yaw
                if input.value < 0:
                    self._matrix = [0, input.value, 0, 0, 0]
                    return np.dot(self._matrix)
                else:
                    self._matrix = [input.value, 0, 0, 0, 0]
            elif input.axis == 1:    #Left-stick, vertical, controls forward,backward
                self._matrix = [0, 0,  input.value, 0, 0]
            elif input.axis == 2:   #Left-trigger, controls submerge
                self._matrix = [0, 0, 0, ((input.value + 1)/2), 0]
            elif input.axis == 5:   #Right-trigger, controls breach
                self._matrix = [0, 0, 0, 0, -((input.value + 1)/2)]

            return self._matrix

    def _run(self):
        '''
        Continuously send Xbox data over the network specified
        '''
        while True:
            for event in pygame.event.get():
                self._send(msg=(self._control(event)), register='RC', local=False, foreign=True)
