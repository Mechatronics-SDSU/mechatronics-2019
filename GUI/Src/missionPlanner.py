from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import pysftp
from PyQt5 import uic
import json
from setGateWidget import SetGate
from waypoint_mission_widget import waypoint_task_GUI

class MissionPlanner(QtWidgets.QWidget):

    #def __init__(self, host, username, password):
    def __init__(self):

        QtWidgets.QWidget.__init__(self)

        #self.host = host
        #self.username = username
        #self.password = password
        #self.server_connection = pysftp.Connection(host=self.host, username=self.username, password=self.password)
        self.foreign_filepath = "mechatronics-2019/Sub/Src/Mission/MissionFiles/tests/"
        self.local_filepath = None
        self.file_list = None

        self.isLoadedMission = False

        #Call in the ui for mission select
        self.task_selector_widget = uic.loadUi("task_selector_widget.ui", self)
        self.task_selector_widget.selectorBox.currentIndexChanged.connect(self.taskSelected)
        self.task_selector_widget.saveButton.clicked.connect(self.saveMission)

    def displayMission(self):

        filename = 'C:/Users/cfior/Desktop/GITS/mechatronics-2019/GUI/Src/MissionFiles/Auto_Test/mission.json'
        with open(filename) as f:
            json_data = json.load(f)
            json_data_new = json.dumps(json_data, indent = 4)
            self.plainTextEdit.setPlainText((str)(json_data_new))

    def getNewMission(self):

        path= os.getcwd()
        print("current directory" + (str)(path))
        self.setTaskNumber = 1

    def taskSelected(self):

        if self.task_selector_widget.selectorBox.currentIndex() == 2:
            self.set_gate_no_vision_selected()
        elif self.task_selector_widget.selectorBox.currentIndex() == 0:
            self.waypoint_task_selected()

    def set_gate_no_vision_selected(self):
        #Call in the ui for set_gate_no_vision_widget
        self.set_gate = SetGate()
        self.set_gate.show()
        self.set_gate.isLoadedMission = self.isLoadedMission
        self.set_gate.filePath =  'C:/Users/cfior/Desktop/GITS/mechatronics-2019/GUI/Src/exampleGateMission.json' #ADD FILE PATH HERE
        self.set_gate.setGateData()

    def waypoint_task_selected(self):

        #Call in the ui for waypoint_task_widget
        self.waypoint = waypoint_task_GUI()
        self.waypoint.show()
        self.waypoint.isLoadedMission = self.isLoadedMission
        self.waypoint.filePath = 'C:/Users/cfior/Desktop/GITS/mechatronics-2019/GUI/Src/exampleWaypointTask.json' #ADD FILE PATH HERE
        self.waypoint.setWaypointData()

    def send_file(self):
        index = self.local_filepath.rfind('/')
        try:
            self.server_connection.put(self.local_filepath, self.foreign_filepath + (self.local_filepath[index::]))
        except Exception as e:
            print("[ERROR]: File not found!!!", e)

    def receive_file(self):
        self.file_list = self.server_connection.listdir(self.foreign_filepath)
        for filename in self.file_list:
            if filename.endswith('.json'):
                try:
                    self.server_connection.get(self.foreign_filepath + filename, self.local_filepath + filename)
                except Exception as e:
                    print("[ERROR]: Filepath not found!!!", e)

    def kill_connection(self):
        self.server_connection.close()

    def saveMission(self):
        text = self.plainTextEdit.toPlainText()
        #SAVE TEXT TO MISSION FILE


if __name__ == "__main__":

    main_app = QtWidgets.QApplication([])
    main_app.setStyle('Fusion')

    main_widget = MissionPlanner("192.168.1.14", "nvidia", "nvidia")
    main_widget.resize(1000, 1000)

    main_widget.show()

    sys.exit(main_app.exec_())
