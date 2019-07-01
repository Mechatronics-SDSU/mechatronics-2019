'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 06/29/2019
Description: This module allows to record waypoints. Should typically be used in
            conjunction with the remote control widget.
'''
import os
import sys

PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from MechOS import mechos

PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import navigation_data_pb2

import struct

class Waypoint_GUI(QWidget):
    '''
    '''
    def __init__(self):
        QWidget.__init__(self)

        #Set the background color of the widget
        #waypoint_gui_palette = self.palette()
        #waypoint_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        #self.setPalette(waypoint_gui_palette)

        #Get mechos network configurations
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS parameter server (this is where we will save the waypoint file)
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #Call in ui waypoint_widget design (build in QtDesigner)
        self.waypoint_widget = uic.loadUi("waypoint_widget.ui", self)

        self.waypoint_widget.enable_waypoint_collection_checkbox.stateChanged.connect(self._update_waypoint_enable)

        #Create a mechos network publisher to publish the enable state of the
        #waypoints
        self.waypoint_node = mechos.Node("Waypoint Node", configs["ip"])
        self.waypoint_control_publisher = self.waypoint_node.create_publisher("WYP", configs["pub_port"])

        #Connect button to save button to the parameter server.
        self.waypoint_widget.save_waypoint_file_btn.clicked.connect(self._update_save_waypoint_file)
        currently_set_waypoint_file = self.param_serv.get_param("Missions/waypoint_collect_file")
        self.waypoint_widget.waypoint_file_line_edit.setText(currently_set_waypoint_file)

        #Send disable waypoint message on start up.
        self._update_waypoint_enable()

        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)
        #self.linking_layout.addWidget(self.waypoint_widget, 0, 0)

        self.setMinimumSize(449, 330)



    def _update_waypoint_enable(self):
        '''
        Update telling the sub if should enable waypoint checking mode.

        Parameters:
            N/a
        Returns:
            N/A
        '''
        #If the box is checked, send enable waypoint to sub.
        if(self.waypoint_widget.enable_waypoint_collection_checkbox.isChecked()):
            enable_waypoint_state = struct.pack('b', 1)
            self.waypoint_control_publisher.publish(enable_waypoint_state)
            self.waypoint_widget.waypoint_info_text_edit.append("[INFO]: Waypoint Mode Enabled")

        #Else disable the ability to capture of waypoints.
        else:
            enable_waypoint_state = struct.pack('b', 0)
            self.waypoint_control_publisher.publish(enable_waypoint_state)
            self.waypoint_widget.waypoint_info_text_edit.append("[INFO]: Waypoint Mode Disabled")

    def _update_save_waypoint_file(self):
        '''
        Update the Waypoint Save file to the parameter server.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        waypoint_save_file = self.waypoint_widget.waypoint_file_line_edit.text()

        #Print information to the text edit box
        self.waypoint_widget.waypoint_info_text_edit.append("[INFO]: Setting Waypoint file as:")
        self.waypoint_widget.waypoint_info_text_edit.append("\t%s" % waypoint_save_file)

        #Save the waypoint save file to the parameter server.
        self.param_serv.set_param("Missions/waypoint_collect_file", waypoint_save_file)

        self._update_waypoint_enable()

if __name__ == "__main__":
    main_app = QApplication([])
    main_app.setStyle('Fusion')
    main_widget = Waypoint_GUI()
    print(main_widget.size())
    sys.exit(main_app.exec_())
