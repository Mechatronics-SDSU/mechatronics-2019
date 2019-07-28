'''
Copyright 2019, Ramiz Hanan, All rights reserved

Author: Ramiz Hanan <ramizhanan@gmail.com>

Description: This module allows to choose between loading existing mission or creating new one
'''
import os
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer


class mission_planner_main_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the mission planner GUI

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self.main_menu()

    def main_menu(self):
        '''
        Set up the layout grid for displaying mission planner main menu

        Parameters:
            N/A

        Returns:
            N/A
        '''
        orientation_txt = QLabel("<font color='black'>MISSION PLANNER</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        self.orientation_layout = QGridLayout()

        self.select_load_button = QPushButton("Load Mission")
        self.select_load_button.setStyleSheet("background-color:#999900; color:#E8FFE8")

        self.select_new_button = QPushButton("New Mission")
        self.select_new_button.setStyleSheet("background-color:#2A7E43; color:#E8FFE8")
        #self.select_load_button.clicked.connect(self.mission_editor("load")) #connect here
        #self.select_new_button.clicked.connect(self.mission_editor("new")) #connect here


        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.select_load_button, 0, 0)
        self.orientation_layout.addWidget(self.select_new_button, 0, 1)
        
        self.linking_layout.addLayout(self.orientation_layout, 1)

if __name__ == "__main__":
    main_app = QApplication([])
    main_app.setStyle('Fusion')
    main_widget = mission_planner_main_GUI()
    main_widget.show()
    sys.exit(main_app.exec_())
