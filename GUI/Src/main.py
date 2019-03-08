import sys
import os
PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from MechOS import mechos

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QComboBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from real_time_plotter_widget import Real_Time_Plotter
from nav_odometery_widget import Navigation_GUI
from pid_tuner_widget import PID_Tuner_Widget
from thruster_test_widget import Thruster_Test
import struct

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
        self.main_layout = QGridLayout(self)
        self.secondary_layout = QVBoxLayout()

        self.main_layout.addLayout(self.secondary_layout, 0, 0)

        #Set the background color of the widget
        main_gui_palette = self.palette()
        main_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(main_gui_palette)

        #Place the navigation, IMU, orientation, and odometery display widget
        self.set_nav_odometery()
        self.set_pid_visualizer()
        self.set_thruster_test_widget()
        self.set_mode_selection_widget()

        #MechOS publisher to send movement mode selection
        self.main_gui_node = mechos.Node("MAIN_GUI")
        self.movement_mode_publisher = self.main_gui_node.create_publisher("MM")

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
        optimal_size = self.nav_odom.sizeHint()
        self.nav_odom.setMaximumSize(optimal_size)
        self.secondary_layout.addWidget(self.nav_odom, 0)

    def set_pid_visualizer(self):
        '''
        Set up the PID visualizer on the main gui.

        Parameters:
            N/A

        Returns:
            N/A
        '''


        self.pid_tuner = PID_Tuner_Widget()
        self.pid_tuner.setEnabled(False)
        optimal_size = self.pid_tuner.sizeHint()
        self.pid_tuner.setMaximumSize(optimal_size)
        self.main_layout.addWidget(self.pid_tuner, 0, 1)

    def set_thruster_test_widget(self):
        self.thruster_test = Thruster_Test()
        optimal_size = self.thruster_test.sizeHint()
        self.thruster_test.setMaximumSize(optimal_size)
        self.secondary_layout.addWidget(self.thruster_test, 1)

    def set_mode_selection_widget(self):
        self.mode_selection_layout = QHBoxLayout()
        self.mode_selection = QComboBox()
        self.mode_selection.addItems(["0: Thruster Test Mode",
                                     "1: PID Test/Tuning Mode"])
        self.mode_selection.currentIndexChanged.connect(self._change_movement_mode)
        self.mode_selection_label = QLabel("Movement Mode Selection:")
        self.mode_selection_label.setStyleSheet("color: white")
        self.mode_selection_layout.addWidget(self.mode_selection_label, 0)
        self.mode_selection_layout.addWidget(self.mode_selection, 1)
        self.secondary_layout.addLayout(self.mode_selection_layout, 2)


    def _change_movement_mode(self):
        '''
        Changes the movement (thrust) control mode of the sub.

        Parameters:
            N/A
        '''
        mode = self.mode_selection.currentIndex()

        if mode == 0:
            self.thruster_test.setEnabled(True)
            self.pid_tuner.setEnabled(False)
        elif mode == 1:
            self.thruster_test.setEnabled(False)
            self.pid_tuner.setEnabled(True)

        mode_serialized = struct.pack('b', mode)
        self.movement_mode_publisher.publish(mode_serialized)



if __name__ == "__main__":

    main_app = QApplication([])
    main_app.setStyle('Fusion')
    main_widget = Main_GUI()
    main_widget.show()
    sys.exit(main_app.exec_())
