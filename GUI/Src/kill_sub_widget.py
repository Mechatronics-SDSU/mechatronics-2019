import sys
import os
import platform
import time

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QCheckBox, QLabel, QSlider, QPushButton
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt

PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs
from MechOS import mechos
import struct

class Kill_Button(QWidget):
    '''
        This class is PyQt widget for toggeling sub kill status.

        Parameter:
        N/A

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
        self.title = "Kill Switch"

        #Set background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)

        #Create widgets main layout
        self.linking_layout = QGridLayout(self)
        self.setLayout(self.linking_layout)
        self.setWindowTitle(self.title)

        #Set the value for kill status
        self.KILL_STATUS = "killed"

        #Init the button
        self.pushButton = QPushButton('Kill Sub', self)
        self.pushButton.setStyleSheet("background-color: red")

        #Connect the update function
        self.pushButton.clicked.connect(self._update_status)
        

        #Create MechOS node
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()
        self.sub_killed_node = mechos.Node("GUI_KILL_STATUS", configs["ip"])
        self.sub_killed_publisher = self.sub_killed_node.create_publisher("KS", configs["pub_port"])

    def _update_status(self):
        '''
        Toggles kill switch.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        if(self.KILL_STATUS == "operational"):
            killed_state = struct.pack('b', 1)
            self.sub_killed_publisher.publish(killed_state)
            self.pushButton.setStyleSheet("background-color: red")
            self.pushButton.setText("Killed")
            self.KILL_STATUS = "killed"
        else:
            killed_state = struct.pack('b', 0)
            self.sub_killed_publisher.publish(killed_state)
            self.pushButton.setStyleSheet("background-color: green")
            self.pushButton.setText("Kill Sub")
            self.KILL_STATUS = "operational"


if __name__ == "__main__":
    import sys
    app = QApplication([])
    button_test_gui = Kill_Button()
    button_test_gui.show()
    sys.exit(app.exec_())
