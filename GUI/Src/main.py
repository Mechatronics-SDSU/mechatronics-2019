import sys
import os
PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from MechOS import mechos
from protoFactory import packageProtobuf
import Mechatronics_pb2

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from real_time_plotter_widget import Real_Time_Plotter
from nav_odometery_widget import Navigation_GUI

class Main_GUI(QWidget):
    '''
    This class is a widget that constructs the entire main gui to operate the sub.
    '''
    def __init__(self):
        '''
        Initialize the main GUI with widgets

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        #creates main GUI layout
        self.layout = QGridLayout(self)

        #Place the navigation, IMU, orientation, and odometery display widget
        self.set_nav_odometery()

        #Set the background color of the widget
        main_gui_palette = self.palette()
        main_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(main_gui_palette)

        #connnect main gui to mechos
        self.GUI_node = mechos.Node("GUI_node")
        self.GUI_node.create_subscriber("AHRS_DATA", self.update_AHRS_data)

        #update GUI every 100 milliseconds
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)


    def set_nav_odometery(self):
        '''
        Set up the navigation and odometery display on the main gui.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.nav_odom = Navigation_GUI()
        self.layout.addWidget(self.nav_odom)

    def update_AHRS_data(self, ahrs_data):
        '''
        This is the callback function for the MechOS ahrs data subscriber to call
        to display the ahrs data on the gui.

        Parameters:
            ahrs_data: The raw protobuf structure for AHRS data

        Returns:
            N/A
        '''
        ahrs_data_proto = Mechatronics_pb2.Mechatronics()
        ahrs_data_proto.ParseFromString(ahrs_data)
        self.nav_odom.update_AHRS_data(ahrs_data_proto.ahrs.yaw, ahrs_data_proto.ahrs.pitch,
                                        ahrs_data_proto.ahrs.roll)

    def update(self):
        '''
        The Main update function for the main gui. Updates all data received through the
        mechos network.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.GUI_node.spinOnce()

if __name__ == "__main__":

    main_app = QApplication([])
    main_widget = Main_GUI()
    main_widget.show()
    sys.exit(main_app.exec_())
