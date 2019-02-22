from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QStackedWidget, QSizePolicy, QSpacerItem, QTextEdit, QLabel, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class Controller_Config(QWidget):

    def __init__(self):
        '''
        Initialize the Controller Button Layout Widget.

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

        #Set Title
        orientation_txt = QLabel("<font color='white'>Controller Button Map</font>")
        orientation_txt.setAlignment(Qt.AlignCenter)
        self.linking_layout.addWidget(orientation_txt, 0)
        
        #Create stack widget to display only either Technical Layout or Gamer Layout
        self.stack = QStackedWidget()
        self.linking_layout.addWidget(self.stack)

        self.technical_layout = QWidget()
        self.gamer_layout = QWidget()        

        self._button_map_technical()
        self._button_map_gamer()

        self.state = "gamer"
        self.toggle()

    def toggle(self):
        '''
        Toggle between Technical and Gamer Layout

        Parameters:
            N/A

        Returns:
            N/A
        '''
        if self.state == "technical":
            self.stack.setCurrentWidget(self.technical_layout)
        elif self.state == "gamer":
            self.stack.setCurrentWidget(self.gamer_layout)

    def _button_map_technical(self):
        '''
        Set up the layout grid for displaying Technical Button Layout

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.orientation_layout = QGridLayout(self.technical_layout)

        #Initialize text boxes and line edit displays
        self.left_trigger_txt = QLabel()
        self.left_trigger_txt.setText("<font color='white'>Left Trigger</font>")
        self.left_trigger_box = QLineEdit()
        self.left_trigger_box.setReadOnly(True)

        self.right_trigger_txt = QLabel()
        self.right_trigger_txt.setText("<font color='white'>Right Trigger</font>")
        self.right_trigger_box = QLineEdit()
        self.right_trigger_box.setReadOnly(True)

        self.left_bumper_txt = QLabel()
        self.left_bumper_txt.setText("<font color='white'>Left Bumper</font>")
        self.left_bumper_box = QLineEdit()
        self.left_bumper_box.setReadOnly(True)

        self.right_bumper_txt = QLabel()
        self.right_bumper_txt.setText("<font color='white'>Right Bumper</font>")
        self.right_bumper_box = QLineEdit()
        self.right_bumper_box.setReadOnly(True)

        self.left_stick_txt = QLabel()
        self.left_stick_txt.setText("<font color='white'>Left Stick</font>")
        self.left_stick_box = QLineEdit()
        self.left_stick_box.setReadOnly(True)

        self.right_stick_txt = QLabel()
        self.right_stick_txt.setText("<font color='white'>Right Stick</font>")
        self.right_stick_box = QLineEdit()
        self.right_stick_box.setReadOnly(True)

        self.b_button_txt = QLabel()
        self.b_button_txt.setText("<font color='white'>B</font>")
        self.b_button_box = QLineEdit()
        self.b_button_box.setReadOnly(True)

        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.left_trigger_txt, 0, 0)
        self.orientation_layout.addWidget(self.left_trigger_box, 0, 1)
        self.orientation_layout.addWidget(self.right_trigger_txt, 0, 3)
        self.orientation_layout.addWidget(self.right_trigger_box, 0, 2 )

        self.orientation_layout.addWidget(self.left_bumper_txt, 1, 0)
        self.orientation_layout.addWidget(self.left_bumper_box, 1, 1)
        self.orientation_layout.addWidget(self.right_bumper_txt, 1, 3)
        self.orientation_layout.addWidget(self.right_bumper_box, 1, 2)

        self.orientation_layout.addWidget(self.left_stick_txt, 2, 0)
        self.orientation_layout.addWidget(self.left_stick_box, 2, 1)
        self.orientation_layout.addWidget(self.right_stick_txt, 2, 3)
        self.orientation_layout.addWidget(self.right_stick_box, 2, 2)

        self.orientation_layout.addWidget(self.b_button_txt, 3, 3)
        self.orientation_layout.addWidget(self.b_button_box, 3, 2)

        self._set_technical_controls()

        self.stack.addWidget(self.technical_layout)

    def _button_map_gamer(self):
        '''
        Set up the layout grid for displaying Gamer Button Layout

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.orientation_layout = QGridLayout(self.gamer_layout)

        #Initialize text boxes and line edit displays
        self.left_stick_up_txt = QLabel()
        self.left_stick_up_txt.setText("<font color='white'>Left Stick Up</font>")
        self.left_stick_up_box = QLineEdit()
        self.left_stick_up_box.setReadOnly(True)

        self.left_stick_left_txt = QLabel()
        self.left_stick_left_txt.setText("<font color='white'>Left Stick Left</font>")
        self.left_stick_left_box = QLineEdit()
        self.left_stick_left_box.setReadOnly(True)

        self.left_stick_right_txt = QLabel()
        self.left_stick_right_txt.setText("<font color='white'>Left Stick Right</font>")
        self.left_stick_right_box = QLineEdit()
        self.left_stick_right_box.setReadOnly(True)

        self.left_stick_down_txt = QLabel()
        self.left_stick_down_txt.setText("<font color='white'>Left Stick Down</font>")
        self.left_stick_down_box = QLineEdit()
        self.left_stick_down_box.setReadOnly(True)

        self.right_stick_x_txt = QLabel()
        self.right_stick_x_txt.setText("<font color='white'>Right Stick X</font>")
        self.right_stick_x_box = QLineEdit()
        self.right_stick_x_box.setReadOnly(True)

        self.right_stick_y_txt = QLabel()
        self.right_stick_y_txt.setText("<font color='white'>Right Stick Y</font>")
        self.right_stick_y_box = QLineEdit()
        self.right_stick_y_box.setReadOnly(True)

        self.b_button_txt = QLabel()
        self.b_button_txt.setText("<font color='white'>B</font>")
        self.b_button_box = QLineEdit()
        self.b_button_box.setReadOnly(True)

        #Add text boxs and line edit displays to layout
        self.orientation_layout.addWidget(self.left_stick_up_txt, 0, 0)
        self.orientation_layout.addWidget(self.left_stick_up_box, 0, 1)
        self.orientation_layout.addWidget(self.left_stick_left_txt, 1, 0)
        self.orientation_layout.addWidget(self.left_stick_left_box, 1, 1 )
        self.orientation_layout.addWidget(self.left_stick_right_txt, 2, 0 )
        self.orientation_layout.addWidget(self.left_stick_right_box, 2, 1 )
        self.orientation_layout.addWidget(self.left_stick_down_txt, 3, 0 )
        self.orientation_layout.addWidget(self.left_stick_down_box, 3, 1 )

        self.orientation_layout.addWidget(self.right_stick_x_txt, 0, 3)
        self.orientation_layout.addWidget(self.right_stick_x_box, 0, 2)
        self.orientation_layout.addWidget(self.right_stick_y_txt, 1, 3)
        self.orientation_layout.addWidget(self.right_stick_y_box, 1, 2)

        self.orientation_layout.addWidget(self.b_button_txt, 2, 3)
        self.orientation_layout.addWidget(self.b_button_box, 2, 2)

        self._set_gamer_controls()

        self.stack.addWidget(self.gamer_layout)

    def _set_technical_controls(self):
        self.left_trigger_box.setText("4, 8, negative")
        self.right_trigger_box.setText("4, 8, positive")
        self.left_bumper_box.setText("2, 6, negative")
        self.right_bumper_box.setText("2, 6, positive")
        self.left_stick_box.setText("1, 7, thrust")
        self.right_stick_box.setText("3, 5, thrust")
        self.b_button_box.setText("Swap Config")

    def _set_gamer_controls(self):
        self.left_stick_up_box.setText("forward")
        self.left_stick_left_box.setText("left")
        self.left_stick_right_box.setText("right")
        self.left_stick_down_box.setText("down")
        self.right_stick_x_box.setText("roll")
        self.right_stick_y_box.setText("pitch")
        self.b_button_box.setText("Swap Config")


if __name__ == "__main__":
    import sys
    app = QApplication([])
    controller_config = Controller_Config()
    controller_config.show()
    sys.exit(app.exec_())