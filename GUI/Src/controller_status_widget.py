<<<<<<< HEAD

=======
    
>>>>>>> bf0125df0fa176e760f65f501c2e53539a18608e
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
from controller_status_thread import Status_Thread

class Joystick_Test(QWidget):
    '''
        This class is PyQt widget for displaying controller connection status.
<<<<<<< HEAD

        Parameter:
        N/A for now. Eventually will be passed JOYSTICK_STATUS and OSTYPE

=======
    
        Parameter:
        N/A for now. Eventually will be passed JOYSTICK_STATUS and OSTYPE
        
>>>>>>> bf0125df0fa176e760f65f501c2e53539a18608e
        Returns:
        N/A
    '''
    def __init__(self):
        '''
            Initialize the layout for the widget by setting its color and instantiating
            its components.
<<<<<<< HEAD

            Parameter:
            N/A

=======
            
            Parameter:
            N/A
            
>>>>>>> bf0125df0fa176e760f65f501c2e53539a18608e
            Returns:
            N/A
        '''
        QWidget.__init__(self)
        self.type = "JOYSTICK_STATUS"
        self.title = 'Joystick Status'
<<<<<<< HEAD

        #Set background color of the widget
        #nav_gui_palette = self.palette()
        #nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        #self.setPalette(nav_gui_palette)

=======
        
        #Set background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)
        
>>>>>>> bf0125df0fa176e760f65f501c2e53539a18608e
        #Create widgets main layout structer
        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)
        self.setWindowTitle(self.title)
<<<<<<< HEAD

        #Set the value for connections status
        #self.JOYSTICK_STATUS = "Connected"
        #self.change_status()

=======
        
        #Set the value for connections status
        #self.JOYSTICK_STATUS = "Connected"
        #self.change_status()
    
>>>>>>> bf0125df0fa176e760f65f501c2e53539a18608e
        #platform.platform()
        #print(platform.system()) #prints Linux, Darwin, or Windows

        self.controller_stat_thread = Status_Thread()
        self.controller_stat_thread.threadrunning = True
        self.controller_stat_thread.start()

        self.controller_stat_thread.valueUpdated.connect(self.change_status)
<<<<<<< HEAD

    def change_status(self):
        '''
        Updates status icon if joystick is connected.

=======
    
    def change_status(self):
        '''
        Updates status icon if joystick is connected.
        
>>>>>>> bf0125df0fa176e760f65f501c2e53539a18608e
        Parameters:
            N/A
        Returns:
            N/A
        '''
        label = QLabel(self)
        if (self.controller_stat_thread.joystickDisconnected == False):
            pixmap = QPixmap('green.png')
        else:
            pixmap = QPixmap('red.png')

        label.setPixmap(pixmap)
        self.resize(pixmap.width()+25, pixmap.height()+25)

if __name__ == "__main__":
    import sys
    app = QApplication([])
    joystick_test_gui = Joystick_Test()
    joystick_test_gui.show()
    sys.exit(app.exec_())
