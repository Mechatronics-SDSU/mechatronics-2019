import sys
import os
import time

from PyQt5.QtCore import QThread

class Webcam_Thread(QThread):

	def __init__(self):
		QThread.__init__(self)
		self.x = 0
		#FIXME: Set up camera/start streaming


	def __del__(self):
		self.wait()

	def run(self):
		#FIXME: Capture pictures at the same FPS as the sub is moving
		while self.threadrunning == True:
			print("Picture " + (str)(self.x))
			self.x = self.x+1
			time.sleep(1)
			#FIXME: Save Pictures



