'''
Copyright 2019, Alexa Becerra, All rights reserved
Author: Alexa Becerra <alexa.becerra99@gmail.com>
Description: Camera node to retrieve images from Point Grey cameras.
'''
import struct
import socket
import pickle
import PySpin
import time
import numpy as np
from message_passing.Nodes.node_base_udp import node_base
import message_passing


class CameraNode(node_base):

	#handles ctr-C for graceful exiting
	def signalHandler(sig, frame):
		print('Exiting')
		self.__deinit__()
		sys.exit(0)

	def __init__(self, IP, MEM):
		node_base.__init__(self, MEM, IP)
		self._system = PySpin.System.GetInstance()
		# Get camera object
		self._cam_list = self._system.GetCameras()
		self._cam = self._cam_list.GetByIndex(0)
		# Initialize camera/Node mode/color format
		self._cam.Init()
		node_map = self._cam.GetNodeMap()

		node_acq_mode = PySpin.CEnumerationPtr(node_map.GetNode('AcquisitionMode'))
		node_acq_mode_cont = node_acq_mode.GetEntryByName('Continuous')
		acq_mode_cont = node_acq_mode_cont.GetValue()
		node_acq_mode.SetIntValue(acq_mode_cont)
		#self._cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8)
		self._cam.BeginAcquisition()

	def _get_image(self):
		image = self._cam.GetNextImage() # Could be raw pointer to struct
		#image_converted = image.Convert(PySpin.PixelFormat_BGR8)
		return image

	def __deinit__(self):
		self._cam.EndAcquisition()
		self._cam.DeInit()
		del self._cam
		self._cam_list.Clear()
		self._system.ReleaseInstance()

	def run(self):
		signal.signal(signal.SIGINT, signalHandler)
		while True:
			self._send(msg=)
