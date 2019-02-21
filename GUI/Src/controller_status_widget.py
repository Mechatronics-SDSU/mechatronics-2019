'''
Copyright 2019, Ramiz Hanan, All rights reserved
Author: Ramiz Hanan<ramizhanan@gmail.com>
Last Modified 02/19/2019
Description: This PyQt widget is for displaying controller connection status.
'''
import sys
import os
import platform
import time

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QCheckBox, QLabel, QSlider
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt

class Joystick_Test(QWidget):
    '''
        This class is PyQt widget for displaying controller connection status.
    
        Parameter:
        N/A for now. Eventually will be passed JOYSTICK_STATUS and OSTYPE
        
        Returns:
        N/A
    '''
    def __init__(self):
        '''
            Initialize the layout for the widget by setting its color and instantiating
            its components.
            
            Parameter:
            N/A
            
            Returns:
            N/A
        '''
        QWidget.__init__(self)
        self.type = "JOYSTICK_STATUS"
        self.title = 'Joystick Status'
        
        #Set background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)
        
        #Create widgets main layout structer
        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)
        self.setWindowTitle(self.title)
        
        #Set the value for connections status
        self.JOYSTICK_STATUS = "Connected"
        self.change_status()
    
        #platform.platform()
        #print(platform.system()) #prints Linux, Darwin, or Windows
    
    def change_status(self):
        '''
        Updates status icon if joystick is connected.
        
        Parameters:
            N/A
        Returns:
            N/A
        '''
        label = QLabel(self)
        if (self.JOYSTICK_STATUS == "Connected"):
            pixmap = QPixmap('green.png')
        else:
            pixmap = QPixmap('red.png')

        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

if __name__ == "__main__":
    import sys
    app = QApplication([])
    joystick_test_gui = Joystick_Test()
    joystick_test_gui.show()
    sys.exit(app.exec_())
