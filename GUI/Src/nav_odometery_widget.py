'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/09/2019
Description: This module is a PyQt5 widget for displaying navigation data such as
            AHRS IMU data, depth data, and odometery data.
'''
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
class Navigation_GUI(QWidget):

    def __init__(self):
        '''
        Initialize the navigation and odometery data display widget.

        Parameters:
            N/A
        '''
        QWidget.__init__(self)

        #Set the background color of the widget

        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)

        self.linking_layout = QVBoxLayout(self)
        self.setLayout(self.linking_layout)
        self._orientation_layout_grid()
        self._earth_pos_layout_grid()
        self._relative_pos_layout_grid()

    def _orientation_layout_grid(self):
        '''
        Set up the layout grid for displaying AHRS orientation data such as
        yaw, pitch, roll.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        orientation_txt = QLabel("<font color='white'>IMU, Orientation, Depth</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        self.orientation_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.yaw_txt = QLabel()
        self.yaw_txt.setText("<font color='white'>YAW</font>")
        self.yaw_box = QLineEdit()

        self.pitch_txt = QLabel()
        self.pitch_txt.setText("<font color='white'>PITCH</font>")
        self.pitch_box = QLineEdit()

        self.roll_txt = QLabel()
        self.roll_txt.setText("<font color='white'>ROLL</font>")
        self.roll_box = QLineEdit()

        self.depth_txt = QLabel()
        self.depth_txt.setText("<font color='white'>DEPTH</font>")
        self.depth_box = QLineEdit()

        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.yaw_txt, 0, 0)
        self.orientation_layout.addWidget(self.yaw_box, 0, 1)
        self.orientation_layout.addWidget(self.pitch_txt, 0, 2)
        self.orientation_layout.addWidget(self.pitch_box, 0, 3)
        self.orientation_layout.addWidget(self.roll_txt, 0, 4)
        self.orientation_layout.addWidget(self.roll_box, 0, 5)
        self.orientation_layout.addWidget(self.depth_txt, 1, 2)
        self.orientation_layout.addWidget(self.depth_box, 1, 3)

        self.linking_layout.addLayout(self.orientation_layout, 1)

    def _earth_pos_layout_grid(self):
        '''
        Set up the layout to display Earth position data. This is X, Y, and Z
        data.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        odometery_txt = QLabel("<font color='white'>Odometery</font>")
        odometery_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(odometery_txt, 2)

        earth_pos_txt = QLabel("<font color='white'>Earth Position</font>")
        self.linking_layout.addWidget(earth_pos_txt, 3)

        self.earth_pos_layout = QGridLayout()

        #Initialize text boxes and line edit displays
        self.x_txt = QLabel()
        self.x_txt.setText("<font color='white'>X</font>")
        self.x_box = QLineEdit()

        self.y_txt = QLabel()
        self.y_txt.setText("<font color='white'>Y</font>")
        self.y_box = QLineEdit()

        self.z_txt = QLabel()
        self.z_txt.setText("<font color='white'>Z</font>")
        self.z_box = QLineEdit()

        #Add text boxs and line edit displays to layout
        self.earth_pos_layout.addWidget(self.x_txt, 0, 0)
        self.earth_pos_layout.addWidget(self.x_box, 0, 1)
        self.earth_pos_layout.addWidget(self.y_txt, 0, 2)
        self.earth_pos_layout.addWidget(self.y_box, 0, 3)
        self.earth_pos_layout.addWidget(self.z_txt, 0, 4)
        self.earth_pos_layout.addWidget(self.z_box, 0, 5)

        self.linking_layout.addLayout(self.earth_pos_layout, 4)

    def _relative_pos_layout_grid(self):
        '''
        Set up the layout to display relative position data. This is X, Y, and Z
        data.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        relative_pos_txt = QLabel("<font color='white'>Relative Position</font>")
        self.linking_layout.addWidget(relative_pos_txt, 5)

        self.relative_pos_layout = QGridLayout()

        self.x_txt = QLabel()
        self.x_txt.setText("<font color='white'>rX</font>")
        self.x_box = QLineEdit()

        self.y_txt = QLabel()
        self.y_txt.setText("<font color='white'>rY</font>")
        self.y_box = QLineEdit()

        self.z_txt = QLabel()
        self.z_txt.setText("<font color='white'>rZ</font>")
        self.z_box = QLineEdit()

        self.relative_pos_layout.addWidget(self.x_txt, 0, 0)
        self.relative_pos_layout.addWidget(self.x_box, 0, 1)
        self.relative_pos_layout.addWidget(self.y_txt, 0, 2)
        self.relative_pos_layout.addWidget(self.y_box, 0, 3)
        self.relative_pos_layout.addWidget(self.z_txt, 0, 4)
        self.relative_pos_layout.addWidget(self.z_box, 0, 5)

        self.linking_layout.addLayout(self.relative_pos_layout, 6)

    def update_AHRS_data(self, yaw, pitch, roll):
        '''
        Update the dispalys for AHRS yaw, pitch, and roll data by setting the
        text for each line edit display.

        Parameters:
            yaw: floating point yaw data
            pitch: floating point pitch data
            roll: floating point roll data

        Returns:
            N/A
        '''
        self.yaw_box.setText("%.2f" % yaw)
        self.pitch_box.setText("%.2f" % pitch)
        self.roll_box.setText("%.2f" % roll)
if __name__ == "__main__":
    import sys
    app = QApplication([])
    nav_gui = Navigation_GUI()
    nav_gui.show()
    sys.exit(app.exec_())