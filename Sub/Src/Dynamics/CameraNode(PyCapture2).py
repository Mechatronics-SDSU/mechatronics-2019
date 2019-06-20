'''
Copyright 2019, Alexa Becerra, All rights reserved
Author: Alexa Becerra <alexa.becerra99@gmail.com>
Description: Camera node to retrieve images from Point Grey cameras.
'''
import struct
import socket
import pickle
import PyCapture2
import time
import numpy as np
from message_passing.Nodes.node_base_udp import node_base
import message_passing
import cv2

class CameraNode(node_base):

	#handles ctr-C for graceful exiting
	def signalHandler(sig, frame):
		print('Exiting')
		self.__deinit__()
		sys.exit(0)

	def __init__(self, IP, MEM):
		node_base.__init__(self, MEM, IP)
		bus = PyCapture2.BusManager()
		cam = bus.getCameraFromIndex(0)
		self._cam = PyCapture2.Camera()
		self._cam.connect(cam)
		self._cam.startCapture()

	def _get_image(self):
		self.image = self._cam.retrieveBuffer()
		image = image.convert(PyCapture2.PIXEL_FORMAT.BGR)
		return image

	def __deinit__(self):
		self._cam.stopCapture()
		self._cam.disconnect()

	def run(self):
		signal.signal(signal.SIGINT, signalHandler)
		while True:
			self._send()
