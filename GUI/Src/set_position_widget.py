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

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from MechOS import mechos

PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import desired_position_pb2

class Set_Desired_Position_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the Desired Position GUI

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        #Set the background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)

        #Set up MechOS network configurations
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS node to receive data from the sub and display it
        self.set_position_node = mechos.Node("SET_POS_GUI", configs["ip"])
        self.set_position_pub = self.set_position_node.create_publisher("DP", configs["pub_port"])

        #Initialize the desired position proto
        self.dest_pos_proto = desired_position_pb2.DESIRED_POS()

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self._desired_position_inputs()

    def _desired_position_inputs(self):
        '''
        Set up the layout grid for displaying AHRS orientation data such as
        yaw, pitch, roll.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        orientation_txt = QLabel("<font color='white'>Set Desired Position</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        self.orientation_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.yaw_txt = QLabel()
        self.yaw_txt.setText("<font color='white'>YAW</font>")
        self.yaw_box = QLineEdit()
        self.yaw_box.setText("0.0")

        self.pitch_txt = QLabel()
        self.pitch_txt.setText("<font color='white'>PITCH</font>")
        self.pitch_box = QLineEdit()
        self.pitch_box.setText("0.0")

        self.roll_txt = QLabel()
        self.roll_txt.setText("<font color='white'>ROLL</font>")
        self.roll_box = QLineEdit()
        self.roll_box.setText("0.0")

        self.depth_txt = QLabel()
        self.depth_txt.setText("<font color='white'>DEPTH</font>")
        self.depth_box = QLineEdit()
        self.depth_box.setText("0.0")

        self.x_txt = QLabel()
        self.x_txt.setText("<font color='white'>X Pos.</font>")
        self.x_box = QLineEdit()
        self.x_box.setText("0.0")

        self.y_txt = QLabel()
        self.y_txt.setText("<font color='white'>Y Pos.</font>")
        self.y_box = QLineEdit()
        self.y_box.setText("0.0")        

        self.send_position_button = QPushButton("Send Desired Pos.")
        self.send_position_button.setStyleSheet("background-color:#2A7E43; color:#81C596")
        self.send_position_button.clicked.connect(self.send_desired_position)

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

        self.linking_layout.addLayout(self.orientation_layout, 1)
    
    def send_desired_position(self):
        '''
        Send the desired positions to the Sub.

        Parameter:
            N/A
        Returns:
            N/A
        '''
        self.dest_pos_proto.roll = float(self.roll_box.text())
        self.dest_pos_proto.pitch = float(self.pitch_box.text())
        self.dest_pos_proto.yaw = float(self.yaw_box.text())
        self.dest_pos_proto.depth = float(self.depth_box.text())
        self.dest_pos_proto.x_pos = float(self.x_box.text())
        self.dest_pos_proto.y_pos = float(self.y_box.text())

        serialized_pos_proto = self.dest_pos_proto.SerializeToString()
        print("Sending Position\n", self.dest_pos_proto)
        self.set_position_pub.publish(serialized_pos_proto) 


if __name__ == "__main__":
    import sys
    app = QApplication([])
    set_pos_gui = Set_Desired_Position_GUI()
    set_pos_gui.show()
    sys.exit(app.exec_())
