'''
Copyright 2019, Mohammad Shafi, All rights reserved
Author: Mohammad Shafi <ma.shafi99@gmail.com>
Description: Successfully maps Xbox inputs to thrusters, whether on the sub
or on the servo testbench
'''
import socket
import pickle
import pygame
import numpy as np
from message_passing.Nodes.node_base_udp import node_base
import message_passing
from Driver.device import maestro

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
        self._matrix = [0, 0, 0]

        self._dot_product_matrix = np.array([[0, 0, 0, 0, 0, 0, 0, 1],
                                            [0, 0, 0, 1, 0, 0, 0, 0],
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
        Parameters:
            input: The pygame event that we pass in to manipulate the thrusters
        '''
        if input.type == pygame.JOYAXISMOTION:
            if input.axis == 0:    #Left-stick, horizontal, controls yaw
                if input.value < 0:
                    self._matrix = [0, -input.value, 0]
                else:
                    self._matrix = [input.value, 0, 0]
            elif input.axis == 1:    #Left-stick, vertical, controls forward,backward
                self._matrix = [input.value,  input.value, 0]
            elif input.axis == 2:   #Left-trigger, controls submerge
                self._matrix = [0, 0, ((input.value + 1)/2)]
            elif input.axis == 5:   #Right-trigger, controls breach
                self._matrix = [0, 0, -((input.value + 1)/2)]

        dot_matrix = self._dot_product(self._matrix)
        byte_matrix = pickle.dumps(dot_matrix)
        print(byte_matrix)
        return byte_matrix

    def run(self):
        '''
        Continuously send Xbox data over the network specified
        Parameters:
            N/A
        Returns:
            N/A
        '''

        while True:
            for event in pygame.event.get():
                self._send(msg=(self._control(event)), register='RC', local=False, foreign=True)

class ThrusterNode(node_base):

    def __init__(self, IP, MEM):
        '''
        This class initializes the sub's thrusters. Also inherits from node_base.
        Accepts the input from the Xbox, and maps them to the correct thruster on
        the sub
        '''
        node_base.__init__(self, MEM, IP)
        self._memory=MEM
        self._ip_route=IP
        self._maestro=maestro()
        self._message = None

    def _set_thrust(self, array):
        '''
        Take the accepted/received array, use the maestro to map to each individual
        thruster. Only go from 0 to 204, so the PWMs never send more than 80 percent
        power to the thrusters
        Parameters:
            array: The array that we receive from from subsriber end. Write each thruster using the maestro
        Returns:
            N/A
        '''
        #print(int(np.interp(array[0], [-1,1], [25,231])))
        self._maestro.set_target(1, int(np.interp(array[0], [-1,1], [25,231])))
        # self._maestro.set_target(2, int(np.interp(array[1], [-1,1], [25,231])))
        self._maestro.set_target(3, int(np.interp(array[2], [-1,1], [25,231])))
        self._maestro.set_target(4, int(np.interp(array[3], [-1,1], [25,231])))
        self._maestro.set_target(5, int(np.interp(array[4], [-1,1], [25,231])))
        # self._maestro.set_target(6, int(np.interp(array[5], [-1,1], [25,231])))
        self._maestro.set_target(7, int(np.interp(array[6], [-1,1], [25,231])))
        self._maestro.set_target(8, int(np.interp(array[7], [-1,1], [25,231])))

        #print('[{},{},{},{}] \r'.format(int(np.interp(array[0], [-1,1], [25,231])), int(np.interp(array[2], [-1,1], [25,231])), int(np.interp(array[4], [-1,1], [25,231])), int(np.interp(array[6], [-1,1], [25,231]))) , end='')

    def run(self):
        '''
        Continuonly accept messages, set the thrust.
        Parameters:
            N/A
        Returns:
            N/A
        '''
        while True:
            self._message = self._recv('RC', local = False)
            real_matrix= pickle.loads(self._message)
            #print(real_matrix)
            self._set_thrust(real_matrix)

if __name__ == '__main__':
    rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('127.0.0.101', 5558)

    thrust_socket.bind((ip_address))

    IP={'RC':
            {
            'address': ip_address,
            'sockets': (rc_socket, thrust_socket),
            'type': 'UDP'
            }
        }
    MEM={'Something':'nothing'}
    remote_node = RemoteControlNode(IP, MEM)
    thrust_node = ThrusterNode(IP, MEM)

    remote_node.start()
    thrust_node.start()
