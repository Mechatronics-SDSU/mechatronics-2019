#!/usr/bin/env python3
import os
import sys
import pygame

dynamics_path = os.path.join("..")
sys.path.append(dynamics_path)

from Alexa.regularControl import Regular, dotProduct
from Shafi.Calibrated_Control import Calibrate, set_thruster_value
from Nodes.node_base import node_base

class rcNode(node_base):
    '''
    def __init__(self, host, topic, type):
        self._host = host
        self._topic = topic
        self._type = type
        self._domain = socket.AF_INET
        self._publishers = {} #Key: port. Value: publisher
        self._subscribers = {}
    '''

    def run(self, msg, addr):
        self._send(msg, addr)


def main():
    remote_control = rcNode('udp://192.168.1.14', "remote control", 'udp')
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
