'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/09/2019
Description: This module is a PyQt5 widget for displaying navigation data such as
            AHRS IMU data, depth data, and odometery data.
'''
import os
import sys

PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from MechOS import mechos
from MechOS.simple_messages.float_array import Float_Array

PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import navigation_data_pb2

class Navigation_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the navigation and odometery data display widget.

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        #Set the background color of the widget

        #nav_gui_palette = self.palette()
        #nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        #self.setPalette(nav_gui_palette)

        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS node to receive data from the sub and display it
        self.sensor_data_node = mechos.Node("NAVIGATION_GUI", '192.168.1.2', '192.168.1.14')
        self.nav_data_subscriber = self.sensor_data_node.create_subscriber("NAV", Float_Array(6), self._update_nav_data, protocol="udp")

        #Initialize the nav data protobuf
        self.nav_data_proto = navigation_data_pb2.NAV_DATA()

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self._orientation_layout_grid()
        self._earth_pos_layout_grid()
        self._relative_pos_layout_grid()

        #Create a timer to update the data
        self.update_nav_data_timer = QTimer()
        self.update_nav_data_timer.timeout.connect(lambda: self.sensor_data_node.spin_once())
        self.update_nav_data_timer.start(1)

    def _orientation_layout_grid(self):
        '''
        Set up the layout grid for displaying AHRS orientation data such as
        yaw, pitch, roll.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        orientation_txt = QLabel("<font color='black'>IMU, Orientation, Depth</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        self.orientation_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.yaw_txt = QLabel()
        self.yaw_txt.setText("<font color='black'>YAW</font>")
        self.yaw_box = QLineEdit()

        self.pitch_txt = QLabel()
        self.pitch_txt.setText("<font color='black'>PITCH</font>")
        self.pitch_box = QLineEdit()

        self.roll_txt = QLabel()
        self.roll_txt.setText("<font color='black'>ROLL</font>")
        self.roll_box = QLineEdit()

        self.depth_txt = QLabel()
        self.depth_txt.setText("<font color='black'>DEPTH</font>")
        self.depth_box = QLineEdit()

        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.yaw_txt, 0, 0)
        self.orientation_layout.addWidget(self.yaw_box, 0, 1)
        self.orientation_layout.addWidget(self.pitch_txt, 0, 2)
        self.orientation_layout.addWidget(self.pitch_box, 0, 3)
        self.orientation_layout.addWidget(self.roll_txt, 0, 4)
        self.orientation_layout.addWidget(self.roll_box, 0, 5)
        self.orientation_layout.addWidget(self.depth_txt, 1, 2)
        self.orientation_layout.addWidget(self.depth_box, 1, 3)

        self.linking_layout.addLayout(self.orientation_layout, 1)

    def _earth_pos_layout_grid(self):
        '''
        Set up the layout to display Earth position data. This is X, Y, and Z
        data.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        odometery_txt = QLabel("<font color='black'>Odometery</font>")
        odometery_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(odometery_txt, 2)

        earth_pos_txt = QLabel("<font color='black'>Earth Position</font>")
        self.linking_layout.addWidget(earth_pos_txt, 3)

        self.earth_pos_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.x_earth_txt = QLabel()
        self.x_earth_txt.setText("<font color='black'>North</font>")
        self.x_earth_box = QLineEdit()

        self.y_earth_txt = QLabel()
        self.y_earth_txt.setText("<font color='black'>East</font>")
        self.y_earth_box = QLineEdit()

        self.z_earth_txt = QLabel()
        self.z_earth_txt.setText("<font color='black'>Z</font>")
        self.z_earth_box = QLineEdit()

        #Add text boxs and line edit displays to layout
        self.earth_pos_layout.addWidget(self.x_earth_txt, 0, 0)
        self.earth_pos_layout.addWidget(self.x_earth_box, 0, 1)
        self.earth_pos_layout.addWidget(self.y_earth_txt, 0, 2)
        self.earth_pos_layout.addWidget(self.y_earth_box, 0, 3)
        self.earth_pos_layout.addWidget(self.z_earth_txt, 0, 4)
        self.earth_pos_layout.addWidget(self.z_earth_box, 0, 5)

        self.linking_layout.addLayout(self.earth_pos_layout, 4)

    def _relative_pos_layout_grid(self):
        '''
        Set up the layout to display relative position data. This is X, Y, and Z
        data.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        relative_pos_txt = QLabel("<font color='black'>Relative Position</font>")
        self.linking_layout.addWidget(relative_pos_txt, 5)

        self.relative_pos_layout = QGridLayout()

        self.x_rel_txt = QLabel()
        self.x_rel_txt.setText("<font color='black'>rX</font>")
        self.x_rel_box = QLineEdit()

        self.y_rel_txt = QLabel()
        self.y_rel_txt.setText("<font color='black'>rY</font>")
        self.y_rel_box = QLineEdit()

        self.z_rel_txt = QLabel()
        self.z_rel_txt.setText("<font color='black'>rZ</font>")
        self.z_rel_box = QLineEdit()

        self.relative_pos_layout.addWidget(self.x_rel_txt, 0, 0)
        self.relative_pos_layout.addWidget(self.x_rel_box, 0, 1)
        self.relative_pos_layout.addWidget(self.y_rel_txt, 0, 2)
        self.relative_pos_layout.addWidget(self.y_rel_box, 0, 3)
        self.relative_pos_layout.addWidget(self.z_rel_txt, 0, 4)
        self.relative_pos_layout.addWidget(self.z_rel_box, 0, 5)

        self.linking_layout.addLayout(self.relative_pos_layout, 6)

    def _update_nav_data(self, nav_data_proto):
        '''
        Update the dispalys for all the navigation data

        Parameters:
            nav_data_proto: The encoded navigation data proto needed to be decoded.

        Returns:
            N/A
        '''
        #print(nav_data_proto, "\n\n")
        #self.nav_data_proto.ParseFromString(nav_data_proto)
        #roll = self.nav_data_proto.roll
        #pitch = self.nav_data_proto.pitch
        #yaw = self.nav_data_proto.yaw
        #depth = self.nav_data_proto.depth
        #x_pos = self.nav_data_proto.north_pos
        #y_pos = self.nav_data_proto.east_pos
        roll, pitch, yaw, depth, x_pos, y_pos = nav_data_proto
        degree_sym = u"\u00b0"
        self.yaw_box.setText('{:6.2f}{}'.format(yaw, degree_sym))
        self.pitch_box.setText('{:6.2f}{}'.format(pitch, degree_sym))
        self.roll_box.setText('{:6.2f}{}'.format(roll, degree_sym))
        self.depth_box.setText('{:6.2f} ft'.format(depth))
        self.z_earth_box.setText('{:6.2f} ft'.format(depth))
        self.x_earth_box.setText('{:6.2f} ft'.format(x_pos))
        self.y_earth_box.setText('{:6.2f} ft'.format(y_pos))

if __name__ == "__main__":
    import sys
    app = QApplication([])
    nav_gui = Navigation_GUI()
    nav_gui.show()
    sys.exit(app.exec_())
