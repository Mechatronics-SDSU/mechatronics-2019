from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
from PyQt5 import uic
import json
from setGateWidget import SetGate
from waypoint_mission_widget import waypoint_task_GUI

class MissionPlanner(QtWidgets.QWidget):

    #def __init__(self, host, username, password):
    def __init__(self):

        QtWidgets.QWidget.__init__(self)

        self.taskNumber = 0
        self.isLoadedMission = False
        #Call in the ui for mission select
        self.task_selector_widget = uic.loadUi("task_selector_widget.ui", self)
        self.task_selector_widget.selectorBox.setCurrentText("Add Task")
        self.task_selector_widget.selectorBox.currentIndexChanged.connect(self.taskSelected)
        self.task_selector_widget.saveButton.clicked.connect(self.saveMission)
        self.task_selector_widget.saveButton_2.clicked.connect(self.refresh)

    def refresh(self):
        cwd = os.getcwd()
        self.filename = '/MissionFiles/' + (str)(self.tempMissionName) + '/mission.json'
        with open(cwd + self.filename) as f:
            json_data = json.load(f)
            json_data_new = json.dumps(json_data, indent = 4)
            self.plainTextEdit.setPlainText((str)(json_data_new))

    def displayMission(self, missionName):
        cwd = os.getcwd()
        self.tempMissionName = missionName
        self.task_selector_widget.listLabel.setText("Loaded mission: " + self.tempMissionName)

        self.filename = '/MissionFiles/' + (str)(self.tempMissionName) + '/mission.json'
        with open(cwd + self.filename) as f:
            json_data = json.load(f)
            json_data_new = json.dumps(json_data, indent = 4)
            self.plainTextEdit.setPlainText((str)(json_data_new))

    def getNewMission(self):

        path= os.getcwd()
        print("current directory" + (str)(path))

    def taskSelected(self):
        self.currentIndex = self.task_selector_widget.selectorBox.currentIndex()
        if self.currentIndex == 2:
            self.set_gate_no_vision_selected()
        elif self.currentIndex == 0:
            self.waypoint_task_selected()

    def set_gate_no_vision_selected(self):
        #Call in the ui for set_gate_no_vision_widget
        self.set_gate = SetGate()
        self.set_gate.show()
        self.set_gate.isLoadedMission = self.isLoadedMission
        self.set_gate.filePath =  os.getcwd() + '/exampleGateMission.json' #ADD FILE PATH HERE
        self.set_gate.setGateData()

    def waypoint_task_selected(self):

        #Call in the ui for waypoint_task_widget
        self.waypoint = waypoint_task_GUI(self.tempMissionName)
        self.waypoint.show()
        self.waypoint.isLoadedMission = self.isLoadedMission
        self.waypoint.filePath = os.getcwd() + '/exampleWaypointTask.json' #ADD FILE PATH HERE
        self.waypoint.setWaypointData()

    def saveMission(self):

        cwd = os.getcwd()
        path = cwd + self.filename
        
        print(str(self.plainTextEdit.toPlainText()))
        with open(path, 'w') as file:
            file.write(str(self.plainTextEdit.toPlainText()))

        #SAVE TEXT TO MISSION FILE


if __name__ == "__main__":

    main_app = QtWidgets.QApplication([])
    main_app.setStyle('Fusion')

    main_widget = MissionPlanner("192.168.1.14", "nvidia", "nvidia")
    main_widget.resize(1000, 1000)

    main_widget.show()

    sys.exit(main_app.exec_())
