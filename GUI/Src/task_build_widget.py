'''
Copyright 2019, Mohammad Shafi, All rights reserved

Author: Mohammad Shafi<ma.shafi99@gmail.com>
        Claire Fiorino

'''
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit
from PyQt5 import uic
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QTimer

class Task_Building_Widget(QWidget):
    '''
    Widget for building and editing missions. Set as many tasks as you want with
    any number of parameters of any time. Output a json file containing mission
    '''
    def __init__(self):
        '''
        Initialize the mission editing widget
        Params:
            N/A
        Returns:
            N/A
        '''
        QWidget.__init__(self)
        self.task_builder_widget = uic.loadUi("task_build_widget.ui", self)
        self.task_builder_widget.save_param_button.clicked.connect(self.add_mission_param)
        self.mission_param_list = []

    def add_mission_param(self):
        '''
        Add a mission parameter to the parameter display list
        Params:
            N/A
        Returns:
            N/A
        '''
        mission_param_string = self.task_builder_widget.param_edit.text()
        mission_val_string = self.task_builder_widget.param_val_edit.text()
        mission_string = mission_param_string + ":" + mission_val_string
        param_model = QStandardItemModel()
        param_model.appendRow(QStandardItem(mission_string))
        self.task_builder_widget.param_list.setModel(param_model)

if __name__ == '__main__':
    main_app = QApplication([])
    main_app.setStyle('Fusion')
    task_widget = Task_Building_Widget()
    task_widget.show()
    sys.exit(main_app.exec_())
