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

class RcThread(QThread):

	def __init__(self):

		QThread.__init__(self)

		configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()
		#MechOS publisher to send movement mode selection
		self.rc_gui_node = mechos.Node("REMOTE_CONTROL", configs["ip"])
		self.rc_mode_publisher = self.rc_gui_node.create_publisher("TT", configs["pub_port"])

		print("THREAD INITIATED")

		#Initialize the remote control proto to package thrust requests
		self.remote_control_proto = thrusters_pb2.Thrusters()

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
					self.Regular(event)
					self.clock.tick(30)

	def Regular(self,XBOX_INPUT):
		'''
		Handles values for thuster control of yaw, pitch and roll motions.
		Parameters:
			XBOX_INPUT: A pygame event
		Returns:
			NumPy array with values of all 8 thrusters.
		'''
		if XBOX_INPUT.type == pygame.JOYAXISMOTION:
			self.InputArray = [0, 0, 0, 0]
			#left stick: x-axis
			if XBOX_INPUT.axis == 0:
				self.InputArray = numpy.array([XBOX_INPUT.value , 0, 0, 0, 0, 0])
				return self.dotProduct()
			#left stick: y-axis
			if XBOX_INPUT.axis == 1:
				self.InputArray = numpy.array([0, XBOX_INPUT.value , 0, 0, 0, 0])
				return self.dotProduct()
			#right stick: x-axis
			if XBOX_INPUT.axis == 2:
				self.InputArray = numpy.array([0, 0 , XBOX_INPUT.value, 0, 0, 0])
				return self.dotProduct()
			#right stick: y-axis
			if XBOX_INPUT.axis == 3:
				self.InputArray = numpy.array([0, 0 , 0, XBOX_INPUT.value, 0, 0])
				return self.dotProduct()
			#left trigger
			if XBOX_INPUT.axis == 4:
				XBOX_INPUT.value = (XBOX_INPUT.value + 1)/2
				self.InputArray = numpy.array([0, 0 , 0, 0, XBOX_INPUT.value, 0])
				return self.dotProduct()
			#right trigger
			if XBOX_INPUT.axis == 5:
				XBOX_INPUT.value = (XBOX_INPUT.value + 1)/2
				self.InputArray = numpy.array([0, 0 , 0, 0, 0, XBOX_INPUT.value])
				return self.dotProduct()
		elif XBOX_INPUT.type == pygame.JOYBUTTONDOWN:
			if XBOX_INPUT.button == 11:
				return "Swap"

	def dotProduct(self): 
		'''
		Performs dot product of the thurster matrix to axis array.
		Parameters:
			Input: Numpy array with axis values
		Return:
			Numpy array with thruster values
		'''
		ThrusterMatrix = numpy.matrix(\
		'0 1 0 0 0 1 0 0 ; \
		0 0 0 -1 0 0 0 -1 ; \
		1 0 1 0 1 0 1 0 ; \
		-1 0 -1 0 -1 0 -1 0; \
		0 -1 0 0 0 1 0 0; \
		0 1 0 0 0 -1 0 0')
		
		InputArray = self.InputArray
		XBOX_OUTPUT = numpy.dot(InputArray,ThrusterMatrix)
		self._update_remote_control_thrust(XBOX_OUTPUT)
		return XBOX_OUTPUT
	
	def _update_remote_control_thrust(self, XBOX_OUTPUT):

		'''
		Parameters:
			N/A
		Returns:
			N/A
		'''

		#Set thruster values to array values
		
		self.remote_control_proto.thruster_1 = int(numpy.interp(XBOX_OUTPUT.item((0,0)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_2 = int(numpy.interp(XBOX_OUTPUT.item((0,1)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_3 = int(numpy.interp(XBOX_OUTPUT.item((0,2)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_4 = int(numpy.interp(XBOX_OUTPUT.item((0,3)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_5 = int(numpy.interp(XBOX_OUTPUT.item((0,4)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_6 = int(numpy.interp(XBOX_OUTPUT.item((0,5)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_7 = int(numpy.interp(XBOX_OUTPUT.item((0,6)),[-1,1],[-100,100]))
		self.remote_control_proto.thruster_8 = int(numpy.interp(XBOX_OUTPUT.item((0,7)),[-1,1],[-100,100]))

		print(self.remote_control_proto.thruster_1)
		print(self.remote_control_proto.thruster_2)
		
		#package test thrust data into a protobuf
		serialized_thruster_data = self.remote_control_proto.SerializeToString()

		#publish data to mechos network
		self.rc_mode_publisher.publish(serialized_thruster_data)