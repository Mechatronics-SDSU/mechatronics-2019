from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import pysftp
from PyQt5 import uic
import json

class SetGate(QtWidgets.QWidget):

    def __init__(self):

        QtWidgets.QWidget.__init__(self)

        #Call in the ui for set_gate_no_vision_widget
        self.set_gate_no_vision = uic.loadUi("set_gate_no_vision_widget.ui", self)
        self.set_gate_no_vision.show()

        self.set_gate_no_vision.pushButton.clicked.connect(self.saveGateTask)

        self.isLoadedMission = False

        self.filePath = None

    def setGateData(self):

        if self.isLoadedMission == True:

            with open(self.filePath, 'r') as json_file:
                self.loaded_gate_data = json.load(json_file)

                self.set_gate_no_vision.lineEdit.setText((str)(self.loaded_gate_data['name'])) #Name
                self.set_gate_no_vision.lineEdit_2.setText((str)(self.loaded_gate_data["timeout"])) #Timeout
                self.set_gate_no_vision.lineEdit_3.setText((str)(self.loaded_gate_data["line_up_position"][0])) #Desired Yaw
                self.set_gate_no_vision.lineEdit_4.setText((str)(self.loaded_gate_data["line_up_position"][1])) #Desired Depth
                self.set_gate_no_vision.lineEdit_5.setText((str)(self.loaded_gate_data["line_up_position"][2])) #Desired X
                self.set_gate_no_vision.lineEdit_6.setText((str)(self.loaded_gate_data["line_up_position"][3])) #Desired Y
                self.set_gate_no_vision.lineEdit_7.setText((str)(self.loaded_gate_data["position_buffer_zone"])) #Pos Buff
                self.set_gate_no_vision.lineEdit_8.setText((str)(self.loaded_gate_data["depth_buffer_zone"])) #Depth Buff
                self.set_gate_no_vision.lineEdit_9.setText((str)(self.loaded_gate_data["yaw_buffer_zone"])) #Yaw Buff
                self.set_gate_no_vision.lineEdit_10.setText((str)(self.loaded_gate_data["stabilization_time"])) #Stabilization time
                self.set_gate_no_vision.lineEdit_11.setText((str)(self.loaded_gate_data["move_forward_dist"])) #Fwd Distance
                #self.set_gate_no_vision.comboBox.setText() #True or false


    def getGateData(self):

        self.name = self.set_gate_no_vision.lineEdit.text() #Name
        self.timeout = self.set_gate_no_vision.lineEdit_2.text() #Timeout
        self.desiredYaw = self.set_gate_no_vision.lineEdit_3.text() #Desired Yaw
        self.desiredDepth = self.set_gate_no_vision.lineEdit_4.text() #Desired Depth
        self.desiredX = self.set_gate_no_vision.lineEdit_5.text() #Desired X
        self.desiredY = self.set_gate_no_vision.lineEdit_6.text() #Desired Y
        self.posBuff = self.set_gate_no_vision.lineEdit_7.text() #Pos Buff
        self.depthBuff = self.set_gate_no_vision.lineEdit_8.text() #Depth Buff
        self.yawBuff = self.set_gate_no_vision.lineEdit_9.text() #Yaw Buff
        self.stabilizationTime = self.set_gate_no_vision.lineEdit_10.text() #Stabilization time
        self.fwdDistance = self.set_gate_no_vision.lineEdit_11.text() #Fwd Distance
        self.torf = self.set_gate_no_vision.comboBox.currentText() #True or false
    
    def saveGateTask(self):

        self.getGateData()

        self.gate_task_data = {"type": "Gate_No_Vision",
        "name": self.name,
        "timeout": self.timeout,
        "line_up_position":[self.desiredYaw, self.desiredDepth, self.desiredX, self.desiredY],
        "position_buffer_zone": self.posBuff,
        "depth_buffer_zone": self.depthBuff,
        "yaw_buffer_zone": self.yawBuff,
        "stabilization_time": self.stabilizationTime, 
        "move_forward_dist": self.fwdDistance,
        "go_through_gate_backwards": self.torf
        }

        #self.gate_task_data_json = json.dumps(self.gate_task_data)

        with open('gateTask.txt', 'w') as json_file:
            json.dump(self.gate_task_data, json_file)

        self.set_gate_no_vision.close()
