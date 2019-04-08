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

from regularControl import RcThread
import numpy

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QComboBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont

from controller_config_widget import Controller_Config
from controller_status_widget import Joystick_Test

class Remote_Control_Widget(QWidget):
	'''
	This class is a widget that displays data from the Remote Control
	'''

	def __init__(self):
		'''
		Initialize the main GUI with widgets

		Parameters:
		N/A

		'''

		QWidget.__init__(self)

		#Creates GUI layout
		self.main_layout = QGridLayout(self)
		self.secondary_layout = QVBoxLayout()

		self.main_layout.addLayout(self.secondary_layout, 0, 0)

		#Set the background color of the widget
		main_gui_palette = self.palette()
		main_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
		self.setPalette(main_gui_palette)

		#Place the controller config widget and the controller status widget on GUI
		self.set_gui_label()
		self.set_controller_status()
		self.set_controller_config()

		#update GUI every 100 milliseconds
		self.update_timer = QTimer()
		self.update_timer.timeout.connect(self.update)
		self.update_timer.start(100)

		#If in RC mode, start thread to read incoming xbox values
		self.start_rc_thread = RcThread()
		self.start_rc_thread.start()

	def set_gui_label(self):
		'''
		Sets label
		'''
		rc_title = QLabel("<font color='white'>Remote Control Mode</font>")
		rc_title.setFont(QFont('SansSerif', 30))
		rc_title.setAlignment(Qt.AlignCenter)
		self.secondary_layout.addWidget(rc_title, 0)

	def set_controller_status(self):
		'''
		Sets controller status on the RC GUI
		'''
		self.controller_stat = Joystick_Test()
		optimal_size = self.controller_stat.sizeHint()
		self.controller_stat.setMaximumSize(optimal_size)
		self.secondary_layout.addWidget(self.controller_stat, 0)

	def set_controller_config(self):
		'''
		Sets controller config on the RC GUI
		'''
		self.controller_conf = Controller_Config()
		optimal_size = self.controller_conf.sizeHint()
		self.controller_conf.setMaximumSize(optimal_size)
		self.secondary_layout.addWidget(self.controller_conf, 0)


if __name__ == "__main__":

	main_app = QApplication([])
	main_app.setStyle('Fusion')
	rc_widget = Remote_Control_Widget()
	rc_widget.show()
	sys.exit(main_app.exec_())
