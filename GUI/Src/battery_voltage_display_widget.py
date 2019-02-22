'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino <clairefiorino@icloud.com>
Last Modified 02/21/2019
Description: This PyQt widget is for displaying battery status and voltage
'''

from PyQt5.QtWidgets import QWidget, QDial, QApplication, QGridLayout, QProgressBar, QTextEdit, QLabel
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QRect

class Battery_Display(QWidget):
    '''
    This class is a PyQt widget for displaying battery left on sub and voltage being used
    test.
    '''
    def __init__(self):
        '''
        Initialize the layout for the widget by setting its color and instantiating
        its components.
        Parameters:
            N/A
        Returns:
            N/A
        '''
        QWidget.__init__(self)

        #Set background color of the widget
        batt_gui_palette = self.palette()
        batt_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(batt_gui_palette)

        #Create widgets main layout structure
        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)

        #Set voltage widget title
        self.batterytitle = QLabel()
        self.batterytitle.setText("<font color='white'>BATTERY</font>")
        self.linking_layout.addWidget(self.batterytitle, 0, 0)

        #Initialize dynamic bar display for battery
        self.batterybar = QProgressBar()
        self.batterybar.setGeometry(QRect(10, 10, 70, 40))
        self.batterybar.setProperty("value", 100)
        self.linking_layout.addWidget(self.batterybar, 0, 1)

        #Initialize dynamic battery percentage label
        self.batterylabel = QLabel()
        val = self.batterybar.value()
        self.batterylabel.setText("%d" % val + "%")
        self.linking_layout.addWidget(self.batterylabel, 0, 2)

        #Set battery widget title
        self.voltagetitle = QLabel()
        self.voltagetitle.setText("<font color='white'>VOLTAGE</font>")
        self.linking_layout.addWidget(self.voltagetitle, 1, 0)

        #Initialize dynamic bar display for voltage
        self.voltagebar = QProgressBar()
        self.voltagebar.setGeometry(QRect(10, 10, 70, 40))
        self.voltagebar.setProperty("value", 0)
        self.linking_layout.addWidget(self.voltagebar, 1, 1)

        #Initialize dynamic voltage label
        self.voltagelabel = QLabel()
        val = self.voltagebar.value()
        self.voltagelabel.setText("%.2f" % val + "V")
        self.linking_layout.addWidget(self.voltagelabel, 1, 2)
    
    def update_battery(self, battery):
        '''
        Updates percentage of battery left
        
        Parameters:
            battery: integer percentage of how much battery is left
        Returns:
            N/A
        '''

        self.batterybar.setProperty("value", battery)
        self.batterybar.QLabel(self.value)
    
    def update_voltage(self, voltage):
        '''
        Updates voltage
        
        Parameters:
            battery: float number of volts
        Returns:
            N/A
        '''
        self.voltagebar.setProperty("value", voltage)
        self.voltagebar.QLabel(self.value)

if __name__ == "__main__":
    import sys
    app = QApplication([])
    battery_disp = Battery_Display()
    battery_disp.show()
    sys.exit(app.exec_())

