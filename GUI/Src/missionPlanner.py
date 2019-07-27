from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
from exVideoWidget import VideoWindow
from webcam_thread import Webcam_Thread
from PyQt5 import uic

class MissionPlanner(QtWidgets.QWidget):
    
    def __init__(self):

        QtWidgets.QWidget.__init__(self)

        #Call in the ui for mission select
        self.task_selector_widget = uic.loadUi("task_selector_widget.ui", self)
        self.task_selector_widget.comboBox.currentIndexChanged.connect(self.taskSelected)
        self.task_selector_widget.findFile.clicked.connect(self.getFile)

    def taskSelected(self):

        if self.task_selector_widget.comboBox.currentIndex() == 2:
            self.set_gate_no_vision_selected()
        elif self.task_selector_widget.comboBox.currentIndex() == 0:
            self.waypoint_task_selected()

    def set_gate_no_vision_selected(self):
        #Call in the ui for set_gate_no_vision_widget
        self.set_gate = SetGate()
        self.set_gate.show()

    def waypoint_task_selected(self):
        #Call in the ui for waypoint_task_widget
        self.waypoint = WaypointTask()
        self.waypoint.show()

    def getFile(self):

        self.dlg = QtWidgets.QFileDialog()
        self.dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)

class SetGate(QtWidgets.QWidget):

    def __init__(self):

        QtWidgets.QWidget.__init__(self)

        #Call in the ui for set_gate_no_vision_widget
        self.set_gate_no_vision = uic.loadUi("set_gate_no_vision_widget.ui", self)
        self.set_gate_no_vision.show()

class WaypointTask(QtWidgets.QWidget):

    def __init__(self):

        QtWidgets.QWidget.__init__(self)

        #Call in the ui for waypoint_task_widget
        self.waypoint_task = uic.loadUi("waypoint_task_widget.ui", self)
        self.waypoint_task.show()


if __name__ == "__main__":

    main_app = QtWidgets.QApplication([])
    main_app.setStyle('Fusion')

    main_widget = MissionPlanner()
    main_widget.resize(1000, 1000)

    main_widget.show()

    sys.exit(main_app.exec_())