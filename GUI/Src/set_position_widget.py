'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 04/05/2019
Description: This module is a PyQt 5 widget used to set the position of the Sub.
'''
import os
import sys

PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

MESSAGE_TYPE_PATH = os.path.join("..", "..", "Message_Types")
sys.path.append(MESSAGE_TYPE_PATH)
from desired_position_message import Desired_Position_Message

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from MechOS import mechos
from MechOS.simple_messages.bool import Bool


class Set_Desired_Position_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the Desired Position GUI

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        #Set the background color of the widget
        #nav_gui_palette = self.palette()
        #nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        #self.setPalette(nav_gui_palette)

        #Set up MechOS network configurations
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS node to receive data from the sub and display it
        self.set_position_node = mechos.Node("SET_POSITION_GUI", '192.168.1.2', '192.168.1.14')
        self.set_position_pub = self.set_position_node.create_publisher("DESIRED_POSITION", Desired_Position_Message(), protocol="tcp")
        self.zero_position_pub = self.set_position_node.create_publisher("ZERO_POSITION", Bool(), protocol="tcp")

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self._desired_position_inputs()

        self.desired_position = [0, 0, 0, 0, 0, 0]

    def _desired_position_inputs(self):
        '''
        Set up the layout grid for displaying AHRS orientation data such as
        yaw, pitch, roll.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        orientation_txt = QLabel("<font color='black'>Set Desired Position</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        self.orientation_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.yaw_txt = QLabel()
        self.yaw_txt.setText("<font color='black'>YAW</font>")
        self.yaw_box = QLineEdit()
        self.yaw_box.setText("0.0")

        self.pitch_txt = QLabel()
        self.pitch_txt.setText("<font color='black'>PITCH</font>")
        self.pitch_box = QLineEdit()
        self.pitch_box.setText("0.0")

        self.roll_txt = QLabel()
        self.roll_txt.setText("<font color='black'>ROLL</font>")
        self.roll_box = QLineEdit()
        self.roll_box.setText("0.0")

        self.depth_txt = QLabel()
        self.depth_txt.setText("<font color='black'>DEPTH</font>")
        self.depth_box = QLineEdit()
        self.depth_box.setText("0.0")

        self.x_txt = QLabel()
        self.x_txt.setText("<font color='black'>North Pos.</font>")
        self.x_box = QLineEdit()
        self.x_box.setText("0.0")

        self.y_txt = QLabel()
        self.y_txt.setText("<font color='black'>East Pos.</font>")
        self.y_box = QLineEdit()
        self.y_box.setText("0.0")

        self.send_position_button = QPushButton("Send Desired Pos.")
        self.send_position_button.setStyleSheet("background-color:#2A7E43; color:#E8FFE8")
        self.send_position_button.clicked.connect(self.send_desired_position)

        #Set current x and y position as [0, 0]
        self.zero_position_button = QPushButton("Zero Position")
        self.zero_position_button.setStyleSheet("background-color:#DBDB3A; color:#5A5A00")
        self.zero_position_button.clicked.connect(self.zero_position)


        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.yaw_txt, 0, 0)
        self.orientation_layout.addWidget(self.yaw_box, 0, 1)
        self.orientation_layout.addWidget(self.pitch_txt, 0, 2)
        self.orientation_layout.addWidget(self.pitch_box, 0, 3)
        self.orientation_layout.addWidget(self.roll_txt, 0, 4)
        self.orientation_layout.addWidget(self.roll_box, 0, 5)
        self.orientation_layout.addWidget(self.depth_txt, 1, 0)
        self.orientation_layout.addWidget(self.depth_box, 1, 1)
        self.orientation_layout.addWidget(self.x_txt, 1, 2)
        self.orientation_layout.addWidget(self.x_box, 1, 3)
        self.orientation_layout.addWidget(self.y_txt, 1, 4)
        self.orientation_layout.addWidget(self.y_box, 1, 5)
        self.orientation_layout.addWidget(self.send_position_button, 2, 3)
        self.orientation_layout.addWidget(self.zero_position_button, 2, 1)
        self.linking_layout.addLayout(self.orientation_layout, 1)

    def send_desired_position(self):
        '''
        Send the desired positions to the Sub.

        Parameter:
            N/A
        Returns:
            N/A
        '''
        self.desired_position[0] = float(self.roll_box.text())
        self.desired_position[1] = float(self.pitch_box.text())
        self.desired_position[2] = float(self.yaw_box.text())
        self.desired_position[3] = float(self.x_box.text())
        self.desired_position[4] = float(self.y_box.text())
        self.desired_position[5] = float(self.depth_box.text())

        print("[INFO]: Sending Position\n", self.desired_position)
        self.set_position_pub.publish(self.desired_position)

    def zero_position(self):
        '''
        Set the set zero position flag to true so that the sub set's it's current
        X and Y position as origin.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #Zero roll, pitch, x, and y to stabilize the sub at origin.

        self.roll_box.setText("0.0")
        self.pitch_box.setText("0.0")
        self.x_box.setText("0.0")
        self.y_box.setText("0.0")

        self.desired_position[0] = 0.0
        self.desired_position[1] = 0.0
        self.desired_position[2] = 0.0
        self.desired_position[3] = 0.0
        self.set_position_pub.publish(self.desired_position)
        self.zero_position_pub.publish(True)
        print("[INFO]: Zeroing Position\n", self.desired_position)

if __name__ == "__main__":
    import sys
    app = QApplication([])
    set_pos_gui = Set_Desired_Position_GUI()
    set_pos_gui.show()
    sys.exit(app.exec_())
