'''
Copyright 2018, Alexa Becerra, All rights reserved
Author: Alexa Becerra <alexa.becerra99@gmail.com>
Description: Regular controls for thruster values.
'''
import sys
import os
PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

import thrusters_pb2

from MechOS import mechos
import pygame
import numpy
from PyQt5.QtCore import QThread

class Status_Thread(QThread):

	def __init__(self):

		QThread.__init__(self)
		self.threadrunning = False

	def __del__(self):
		self.wait()

	def run(self):
			self.clock = pygame.time.Clock()
			pygame.init()
			pygame.joystick.init()
			self.controller = pygame.joystick.Joystick(0)
			self.controller.init()
			while self.threadrunning == True:
				for event in pygame.event.get():
					self.checkStatus()

	def checkStatus(self):
		print("checking status")

