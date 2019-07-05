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
import time

from MechOS import mechos
import pygame
import numpy
from PyQt5.QtCore import QThread
from PyQt5 import QtCore

class Status_Thread(QThread):

	valueUpdated = QtCore.pyqtSignal(bool)

	def __init__(self):
		QThread.__init__(self)
		pygame.joystick.init()
		self.joystickDisconnected = False


	def __del__(self):
		self.wait()

	def run(self):
		while self.threadrunning == True:
			self.checkStatus()
			time.sleep(1)

	def checkStatus(self):
		print("checking status")
		joysticks = [pygame.joystick.Joystick(x) for x in range (pygame.joystick.get_count())]
		if len(joysticks) == 1:
			self.joystickDisconnected = True
		self.valueUpdated.emit(self.joystickDisconnected)

