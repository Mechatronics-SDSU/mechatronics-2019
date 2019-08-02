'''
Copyright 2019, Ramiz HAnan, All rights reserved

Author: Ramiz Hanan<ramizhana@gmail.com>

Description: This module is a PyQt 5 widget used to set the parameters for a waypoint mission.
'''
import os
import json
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer


class waypoint_task_GUI(QWidget):

    def __init__(self, missionName): #pass mission name, task number
        '''
        Initialize the Waypoint task parameter GUI

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self.setFixedWidth(1000)
        self._desired_waypoint_inputs()

        self.isLoadedMission = False
        self.filePath = None
        self.missionName = missionName

    def _desired_waypoint_inputs(self):
        '''
        Set up the layout grid for displaying waypoint parameter inputs

        Parameters:
            N/A

        Returns:
            N/A
        '''
        task_name_txt = QLabel("<font color='black'>Waypoint Task</font>")
        task_name_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(task_name_txt, 0)
        self.orientation_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.name_txt = QLabel()
        self.name_txt.setText("<font color='black'>Name</font>")
        self.name_box = QLineEdit()

        self.timeout_txt = QLabel()
        self.timeout_txt.setText("<font color='black'>Timeout</font>")
        self.timeout_box = QLineEdit()

        self.pos_buff_txt = QLabel()
        self.pos_buff_txt.setText("<font color='black'>Position Buffer Zone</font>")
        self.pos_buff_box = QLineEdit()

        self.depth_buff_txt = QLabel()
        self.depth_buff_txt.setText("<font color='black'>Depth Buffer Zone</font>")
        self.depth_buff_box = QLineEdit()

        self.yaw_buff_txt = QLabel()
        self.yaw_buff_txt.setText("<font color='black'>Yaw Buffer Zone</font>")
        self.yaw_buff_box = QLineEdit()

        self.waypoint_file_txt = QLabel()
        self.waypoint_file_txt.setText("<font color='black'>Waypoint File</font>")
        self.waypoint_file_box = QLineEdit()
        
        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.name_txt, 0, 0)
        self.orientation_layout.addWidget(self.name_box, 0, 1)
        self.orientation_layout.addWidget(self.timeout_txt, 1, 0)
        self.orientation_layout.addWidget(self.timeout_box, 1, 1)
        self.orientation_layout.addWidget(self.pos_buff_txt, 2, 0)
        self.orientation_layout.addWidget(self.pos_buff_box, 2, 1)
        self.orientation_layout.addWidget(self.depth_buff_txt, 3, 0)
        self.orientation_layout.addWidget(self.depth_buff_box, 3, 1)
        self.orientation_layout.addWidget(self.yaw_buff_txt, 4, 0)
        self.orientation_layout.addWidget(self.yaw_buff_box, 4, 1)
        self.orientation_layout.addWidget(self.waypoint_file_txt, 5, 0)
        self.orientation_layout.addWidget(self.waypoint_file_box, 5, 1)
        #self.orientation_layout.addWidget(self.send_position_button, 6, 8)
        #self.orientation_layout.addWidget(self.zero_position_button, 6, 9)
        
        self.select_cancel_button = QPushButton("Cancel task")
        self.select_cancel_button.setStyleSheet("background-color:#999900; color:#E8FFE8")
        self.select_cancel_button.clicked.connect(self.cancel)

        self.select_add_button = QPushButton("Add task")
        self.select_add_button.setStyleSheet("background-color:#2A7E43; color:#E8FFE8")
        self.select_add_button.clicked.connect(self.saveWaypointTask)
        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.select_cancel_button, 6, 0)
        self.orientation_layout.addWidget(self.select_add_button, 6, 1)
        
        self.linking_layout.addLayout(self.orientation_layout, 1)

    def cancel(self):
        self.close()
        
    def getWaypointData(self):
        
        self.name = self.name_box.text() #Name
        self.timeout = float(self.timeout_box.text()) #Timeout needs to be integers/decimals
        self.posBuff = float(self.pos_buff_box.text()) #Pos Buff
        self.depthBuff = float(self.depth_buff_box.text()) #Depth Buff
        self.yawBuff = float(self.yaw_buff_box.text()) #Yaw Buff
        self.waypointPath = self.waypoint_file_box.text() #Waypoint file path
        
    def saveWaypointTask(self):

        self.getWaypointData()

        data = {}

        self.waypoint_data = {"type": "Waypoint",
        "name": self.name,
        "timeout": self.timeout,
        "position_buffer_zone": self.posBuff,
        "depth_buffer_zone": self.depthBuff,
        "yaw_buffer_zone": self.yawBuff,
        "waypoint_file": self.waypointPath 
        }

        cwd = os.getcwd()
        filepath = "/MissionFiles/"+ self.missionName +"/mission.json"
        path = cwd + filepath
        with open(path, 'r') as f:
            data = json.loads(f.read()) #data becomes a dictionary

        #do things with data here
        data['Task_'] = self.waypoint_data

        #and then just write the data back on the file
        with open(path, 'w') as f:
            f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

        self.close()

        '''
        with open(cwd + filepath) as json_file:
            json_decoded = json.load(json_file)

        data['Task_2'] = self.waypoint_data

        with open((cwd + filepath), 'w') as json_file:
            json.dump(json_decoded, json_file)
            '''


    def setWaypointData(self):

        if self.isLoadedMission == True:

            with open(self.filePath, 'r') as json_file:
                self.loaded_waypoint_data = json.load(json_file)

                self.name_box.setText((str)(self.loaded_waypoint_data['name'])) #Name
                self.timeout_box.setText((str)(self.loaded_waypoint_data["timeout"])) #Timeout
                self.pos_buff_box.setText((str)(self.loaded_waypoint_data["position_buffer_zone"])) #Desired Yaw
                self.depth_buff_box.setText((str)(self.loaded_waypoint_data["depth_buffer_zone"])) #Desired Depth
                self.yaw_buff_box.setText((str)(self.loaded_waypoint_data["yaw_buffer_zone"])) #Desired X
                self.waypoint_file_box.setText((str)(self.loaded_waypoint_data["waypoint_file"])) #Desired Y
