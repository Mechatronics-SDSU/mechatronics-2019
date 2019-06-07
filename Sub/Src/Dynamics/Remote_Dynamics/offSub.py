#!/usr/bin/env python3
import os
import sys
import pygame
import pickle

dynamics_path = os.path.join("..")
sys.path.append(dynamics_path)

from Alexa.regularControl import Regular, dotProduct
from Shafi.Calibrated_Control import Calibrate, set_thruster_value
from NodeClass import Node

class rcNode(Node):
    '''
    def __init__(self):
        super(rcNode,self).__init__()
    '''
    def run(self, message, port):
        letter = pickle.dumps(message)
        (self._publishers[port]).serial_publish(letter)

def main():
    remote_control = rcNode('127.0.0.1', "remote control", 'udp')
    isRegular = False #Calibrate will run first
    remote_control.add_publisher(5558, 'udp', 0.001)
    clock = pygame.time.Clock()
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    while True:
        for event in pygame.event.get():
            if Calibrate(event) is "SWAP":
                isRegular = True
            elif Regular(event) is "SWAP":
                isRegular = False
            else:
                if isRegular is False:
                    remote_control.run((Calibrate(event)), 5558)
                else:
                    remote_control.run((Regular(event)), 5558)

if __name__ == '__main__':
    main()
