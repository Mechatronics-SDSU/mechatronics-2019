#!/usr/bin/env python3

from Shafi.Calibrated_Control import Calibrate
from thruster import thruster
from Driver.device import maestro
import struct
import numpy as np

class Thrusters:
	def __init__(self):
		self.Maestro=maestro()

	def recv_thrust(self, array):

		self.Maestro.set_target(1, int(np.interp(array[0][0], [-1, 1], [0, 254])))
		self.Maestro.set_target(2, int(np.interp(array[0][1], [-1, 1], [0, 254])) )
		self.Maestro.set_target(3, int(np.interp(array[0][2], [-1, 1], [0, 254])) )
		self.Maestro.set_target(4, int(np.interp(array[0][3], [-1, 1], [0, 254])))
		self.Maestro.set_target(5, int(np.interp(array[0][4], [-1, 1], [0, 254])))
		self.Maestro.set_target(6, int(np.interp(array[0][5], [-1, 1], [0, 254])))
		self.Maestro.set_target(7, int(np.interp(array[0][6], [-1, 1], [0, 254])))
		self.Maestro.set_target(8, int(np.interp(array[0][7], [-1, 1], [0, 254])))


if __name__=='__main__':
	import pygame
	from Alexa.regularControl import Regular

	thrusterObject=Thrusters()
	pygame.init()
	pygame.joystick.init()
	controller = pygame.joystick.Joystick(0)
	controller.init()
	while True:
		for event in pygame.event.get():
			thrusterObject.recv_thrust(Calibrate(event).A)
