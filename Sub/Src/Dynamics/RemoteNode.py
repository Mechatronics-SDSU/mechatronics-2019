from Shafi.Calibrated_Control import Calibrate
from Alexa.regularControl import Regular
from message_passing.Nodes.node_base import node_base
import pygame
import numpy as np


class RemoteNode(node_base):
    def __init__(self, memory, ip_router):
        node_base.__init__(self, memory, ip_router)
        pygame.init()
        pygame.joystick.init()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        # Starting in 'Calibrated Mode'
        self.isRegular=False

    def run(self):
        while True:
            for event in pygame.event.get():
                if Calibrate(event) == "SWAP":
                    self.isRegular = True
                elif Regular(event) == "SWAP":
                    self.isRegular = False
                else:
                    if self.isRegular is False:
                        self._send((Calibrate(event).A), 'Thrusters')
                    else:
                        self._send((Regular(event).A), 'Thrusters')
