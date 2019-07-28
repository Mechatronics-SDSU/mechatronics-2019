import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtCore import pyqtSlot, Qt

PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs
from MechOS import mechos
from MechOS.simple_messages.int import Int
from MechOS.simple_messages.bool import Bool
import struct


class Tabbed_Display(QWidget):

    def __init__(self):
        '''
        Initializes a Tabbed Display widget.

        Parameters:
            individual_tab: The individual_tab Qwidget
        '''
        QWidget.__init__(self)
        self.layout = QVBoxLayout(self)

        # Set the background color of the widget
        #tabbed_display_palette = self.palette()
        #tabbed_display_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        #self.setPalette(tabbed_display_palette)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setFixedSize(700, 700)

        # Set color of QTabWidget
        #tabs_palette = self.tabs.palette()
        #tabs_palette.setColor(QPalette.Window, QColor(64, 64, 64))
        #self.tabs.setPalette(tabs_palette)

        # Add tabs to layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Call method _update_mode() when tab is changed
        self.tabs.currentChanged.connect(self._update_mode)

        # Create MechOS node
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()
        self.tab_display_node = mechos.Node("MOVEMENT_MODE_TABS_GUI", '192.168.1.2', '192.168.1.14')
        self.movement_mode_publisher = self.tab_display_node.create_publisher("MOVEMENT_MODE", Int(), protocol="tcp")

        #Publisher to kill the sub when tabs are switched.
        self.sub_killed_publisher = self.tab_display_node.create_publisher("KILL_SUB", Bool(), protocol="tcp")


    def add_tab(self, widget, title):
        '''
        Creates a new tab and adds a Qwidget to it.

        Parameters:
            widget: The Qwidget to be displayed.
            title: (string) The title of the Tab

        Returns:
            N/A
        '''
        # Init individual_tab widget
        individual_tab = QWidget()
        layout = QVBoxLayout(individual_tab)

        # Set color
        #background = individual_tab.palette()
        #background.setColor(QPalette.Window, QColor(64, 64, 64))
        #individual_tab.setPalette(background)
        #individual_tab.setAutoFillBackground(True)

        # Add widget to individual_tab
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(widget)
        individual_tab.setLayout(layout)

        # Add individual_tab to tab
        self.tabs.addTab(individual_tab, title)
        widget.setEnabled(True)
        widget.setAutoFillBackground(True)

    def _update_mode(self):
        '''
        Publishes the current tab index.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        # Get current index
        mode = self.tabs.currentIndex()

        # Publish current index
        self.movement_mode_publisher.publish(mode)

        #Kill the sub when a tab changes
        self.sub_killed_publisher.publish(1)


if __name__ == "__main__":
    from pid_tuner_widget import PID_Tuner_Widget
    from thruster_test_widget import Thruster_Test
    import sys

    app = QApplication([])
    tabbed_display = Tabbed_Display()
    tabbed_display.add_tab(PID_Tuner_Widget(), "PID Tuner")
    tabbed_display.add_tab(Thruster_Test(), "Thusters")
    tabbed_display.show()
    sys.exit(app.exec_())
