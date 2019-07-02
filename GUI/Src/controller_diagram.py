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
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QRect

class Controller_Diagram(QWidget):
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
        self.type = "LABELED_CONTROLLER"
        self.title = 'Labeled Controller'
        
        #Set background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)
        
        #Create widgets main layout structer
        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)
        self.setWindowTitle(self.title)
        self.setGeometry(0,0,400,250)

        label = QLabel(self)
        label.setGeometry(QRect(0,0,400,250))

        pixmap = QPixmap('labeledcontroller.png')
        picscaled = pixmap.scaled(450,375,Qt.KeepAspectRatio)
        label.setPixmap(picscaled)

if __name__ == "__main__":

        import sys
        app = QApplication([])
        controller_diag = Controller_Diagram()
        controller_diag.show()
        sys.exit(app.exec_())
