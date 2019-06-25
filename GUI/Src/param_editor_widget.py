'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino<clairefiorino@icloud.com>
Last Modified 04/09/2019
Description: This PyQt widget displays the labeled configuration of the xbox controller.
'''
import sys
import os
import platform
import time

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt, QRect, QSize

class Param_Editor(QWidget):
    '''
    This class is PyQt widget for displaying what each button on the joystick does
    
    Parameter:
    N/A 
    
    Returns:
    N/A
    '''
    def __init__(self):
        '''
        Initialize the labeled controller diagram on the GUI
            
        Parameter:
        N/A
            
        Returns:
        N/A
        '''
        QWidget.__init__(self)
        
        #Set background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)

        #Set path of xml text file
        self.filePath = "C:/Users/cfior/Desktop/GITS/mechatronics-2019/Sub/Src/Params/mechos_network_configs.txt"

        #Create widgets main layout structure
        self.param_layout = QGridLayout(self)
        self.setLayout(self.param_layout)
        self.title = "Edit Sub Parameters"
        self.setWindowTitle(self.title)

        #set param lables
        self.param_labels()

    def param_labels(self):

        #Initialize layout for each of the params
        self.ip_layout = QHBoxLayout(self)

        self.pubport_layout = QHBoxLayout(self)

        self.subport_layout = QHBoxLayout(self)

        self.paramport_layout = QHBoxLayout(self)

        self.xmlrpc_layout = QHBoxLayout(self) 

        #Get pre-existing param values
        self.fileName = self.filePath
        with open (self.fileName, "r+") as file:
            lines=file.readlines()
        
        #IP
        #Set ip label
        self.ipLabel = QLabel()
        self.ipLabel.setText("<font color='white' size=5>ip: </font>")
        self.ip_layout.addWidget(self.ipLabel)

        #Set ip text box
        self.iptext = QLineEdit()
        self.iptext.setText(lines[0].split(":")[1])
        self.iptext.resize(280,40)
        self.ip_layout.addWidget(self.iptext)

        #Set ip button
        self.ipbutton = QPushButton("Submit")
        self.ipbutton.setCheckable(True)
        self.ipbutton.toggle()
        self.ipbutton.clicked.connect(self.ipclickMethod)
        self.ipbutton.resize(280,40)
        self.ip_layout.addWidget(self.ipbutton)

        #PUB_PORT
        #Set pub_port label
        self.pubportLabel = QLabel()
        self.pubportLabel.setText("<font color='white' size=5>pub_port: </font>")
        self.pubport_layout.addWidget(self.pubportLabel)

        #Set pub_port text box
        self.pubporttext = QLineEdit()
        self.pubporttext.setText(lines[1].split(":")[1])
        self.pubporttext.resize(280,40)
        self.pubport_layout.addWidget(self.pubporttext)

        #Set pub_port button
        self.pubportbutton = QPushButton("Submit")
        self.pubportbutton.setCheckable(True)
        self.pubportbutton.toggle()
        self.pubportbutton.clicked.connect(self.pubportclickMethod)
        self.pubportbutton.resize(280,40)
        self.pubport_layout.addWidget(self.pubportbutton)

        #SUB_PORT
        #Set sub_port label
        self.subportLabel = QLabel()
        self.subportLabel.setText("<font color='white' size=5>sub_port: </font>")
        self.subport_layout.addWidget(self.subportLabel)

        #Set sub_port text box
        self.subporttext = QLineEdit()
        self.subporttext.setText(lines[2].split(":")[1])
        self.subporttext.resize(280,40)
        self.subport_layout.addWidget(self.subporttext)

        #Set sub_port button
        self.subportbutton = QPushButton("Submit")
        self.subportbutton.setCheckable(True)
        self.subportbutton.toggle()
        self.subportbutton.clicked.connect(self.subportclickMethod)
        self.subportbutton.resize(280,40)
        self.subport_layout.addWidget(self.subportbutton)

        #PARAM_PORT
        #Set param_port label
        self.paramportLabel = QLabel()
        self.paramportLabel.setText("<font color='white' size=5>param_port: </font>")
        self.paramport_layout.addWidget(self.paramportLabel)

        #Set param_port text box
        self.paramporttext = QLineEdit()
        self.paramporttext.setText(lines[3].split(":")[1])
        self.paramporttext.resize(280,40)
        self.paramport_layout.addWidget(self.paramporttext)

        #Set param_port button
        self.paramportbutton = QPushButton("Submit")
        self.paramportbutton.setCheckable(True)
        self.paramportbutton.toggle()
        self.paramportbutton.clicked.connect(self.paramportclickMethod)
        self.paramportbutton.resize(280,40)
        self.paramport_layout.addWidget(self.paramportbutton)

        #XMLRPC
        #Set xmlrpc_server_path label
        self.xmlrpcLabel = QLabel()
        self.xmlrpcLabel.setText("<font color='white' size=5>xmlrpc server path: </font>")
        self.xmlrpc_layout.addWidget(self.xmlrpcLabel)

        #Set xmlrpc_server_path text box
        self.xmlrpctext = QLineEdit()
        self.xmlrpctext.setText(lines[4].split(":")[1])
        self.xmlrpctext.resize(280,40)
        self.xmlrpc_layout.addWidget(self.xmlrpctext)

        #Set xmlrpc_server_path button
        self.xmlrpcbutton = QPushButton("Submit")
        self.xmlrpcbutton.setCheckable(True)
        self.xmlrpcbutton.toggle()
        self.xmlrpcbutton.clicked.connect(self.xmlrpcclickMethod)
        self.xmlrpcbutton.resize(280,40)
        self.xmlrpc_layout.addWidget(self.xmlrpcbutton)

        #Add all layouts to main layout
        self.param_layout.addLayout(self.ip_layout,0,0)
        self.param_layout.addLayout(self.pubport_layout,1,0) 
        self.param_layout.addLayout(self.subport_layout,2,0)
        self.param_layout.addLayout(self.paramport_layout,3,0)
        self.param_layout.addLayout(self.xmlrpc_layout,4,0)

    def ipclickMethod(self):

        self.fileName = self.filePath
        with open (self.fileName, "r+") as file:
            lines=file.readlines()
            lines[0] = "ip:"+self.iptext.text()+"\n"

        with open (self.fileName, "w") as file:
            file.writelines(lines)

    def pubportclickMethod(self):

        self.fileName = self.filePath
        with open (self.fileName, "r+") as file:
            lines=file.readlines()
            lines[1] = "pub_port:"+self.pubporttext.text()+"\n"

        with open (self.fileName, "w") as file:
            file.writelines(lines)

    def subportclickMethod(self):
        
        self.fileName = self.filePath
        with open (self.fileName, "r+") as file:
            lines=file.readlines()
            lines[2] = "sub_port:"+self.subporttext.text()+"\n"

        with open (self.fileName, "w") as file:
            file.writelines(lines)

    def paramportclickMethod(self):
        
        self.fileName = self.filePath
        with open (self.fileName, "r+") as file:
            lines=file.readlines()
            lines[3] = "ip:"+self.paramporttext.text()+"\n"

        with open (self.fileName, "w") as file:
            file.writelines(lines)

    def xmlrpcclickMethod(self):
        
        self.fileName = self.filePath
        with open (self.fileName, "r+") as file:
            lines=file.readlines()
            lines[4] = "xmlrpc_server_path:"+self.iptext.text()+"\n"

        with open (self.fileName, "w") as file:
            file.writelines(lines)
    

if __name__ == "__main__":
        import sys
        app = QApplication([])
        param_edit = Param_Editor()
        param_edit.resize(1000,500)
        param_edit.show()
        sys.exit(app.exec_())