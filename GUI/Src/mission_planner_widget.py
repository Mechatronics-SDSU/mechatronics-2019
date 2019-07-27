'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 07/05/2019
Description: This widget control the mission selection and control.
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
from MechOS.simple_messages.bool import Bool
import struct

class Mission_Planner_Widget(QWidget):
    '''
    Widget for mission planning. Select which missions to run.
    '''
    def __init__(self):
        '''
        Initialize the mission planning widget.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        QWidget.__init__(self)

        #Get mechos network configurations
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #MechOS parameter server (this is where we will save the waypoint file)
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #Call in the ui for mission select
        self.mission_select_widget = uic.loadUi("mission_select.ui", self)

        self.mission_select_node = mechos.Node("Mission Select", '192.168.1.2', '192.168.1.14')
        self.update_mission_info_publisher = self.mission_select_node.create_publisher("MS", Bool(), protocol="tcp")

        #Connect the mission select button to update the mission in the parameter
        #server and tell the mission commander that the mission file has changed.
        self.mission_select_widget.save_mission_btn.clicked.connect(self._update_mission_file)
        currently_set_mission_file = self.param_serv.get_param("Missions/mission_file")
        self.mission_select_widget.mission_file_line_edit.setText(currently_set_mission_file)

        self._update_mission_file()

        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)

        self.setMinimumSize(449, 330)

    def _update_mission_file(self):
        '''
        If the Save Mission File button is pressed. Update the parameter server
        with that mission file and tell the sub that the mission file has changed.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        mission_file = self.mission_select_widget.mission_file_line_edit.text()

        #Print information to the text edit box
        self.mission_select_widget.mission_info_text_edit.append("[INFO]: Setting Current Mission to:")
        self.mission_select_widget.mission_info_text_edit.append("\t%s" % mission_file)

        self.param_serv.set_param("Missions/mission_file", mission_file)

        #Tell the sub to update it's mission information
        self.update_mission_info_publisher.publish(True)

if __name__ == "__main__":
    main_app = QApplication([])
    main_app.setStyle('Fusion')
    main_widget = Mission_Planner_Widget()
    sys.exit(main_app.exec_())
