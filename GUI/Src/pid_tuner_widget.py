'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 03/01/2019
Description: This PyQt widget is for tunning the PID controls.
'''
import sys
import os
from MechOS import mechos


PARAM_PATH = os.path.join("..", "..", "Sub", "Src", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QCheckBox, QLabel, QSlider
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QComboBox, QPushButton
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
import time
from real_time_plotter_widget import Real_Time_Plotter
from set_position_widget import Set_Desired_Position_GUI

class PID_Tuner_Widget(QWidget):
    '''
    This class is a PyQt widget for tunning the 6 degree of freedom PID control system.
    '''
    def __init__(self):
        '''
        Initialize the layout for the widget by setting its color and instantiating its
        components:

        Parameters:
            N/A

        Returns:
            N/A
        '''
        QWidget.__init__(self)

        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #self.pid_gui_node = mechos.Node("PID_GUI", configs["ip"])

        #Publisher to tell the navigation/movement controller when new PID values are saved.
        self.pid_configs_update_publisher = self.pid_gui_node.create_publisher("PID", '192.168.1.2', '192.168.1.14')

        #Subscriber to get PID ERRORS
        #self.pid_errors_subscriber = self.pid_gui_node.create_subscriber("PE", self._update_error_plot, configs["sub_port"])
        #self.pid_error_proto = pid_errors_pb2.PID_ERRORS()

        #Mechos parameter server
        #Initialize parameter server client to get and set parameters related to sub
        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])


        #Set background color of the widget
        #nav_gui_palette = self.palette()
        #nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        #self.setPalette(nav_gui_palette)

        #Create widgets main layout structure
        self.primary_linking_layout = QVBoxLayout(self)
        self.setLayout(self.primary_linking_layout)

        #Options widget
        self.options_linking_layout = QGridLayout()

        self._error_plotter()
        self._PID_controller_select()
        self._PID_sliders()
        self.set_desired_position = Set_Desired_Position_GUI()


        #Set up QTimer to update the PID errors
        self.pid_error_update_timer = QTimer()

        self.pid_error_update_timer.timeout.connect(lambda: self.pid_gui_node.spinOnce(self.pid_errors_subscriber))

        self.primary_linking_layout.addLayout(self.options_linking_layout, 1)
        self.primary_linking_layout.addWidget(self.set_desired_position, 2)
        #Start PID errors update errors. Update 100 timers a second
        self.pid_error_update_timer.start(10)


    def _PID_controller_select(self):
        '''
        '''
        self.PID_controller_layout = QGridLayout()

        #A combo box to select which PID channel to tune
        self.pid_channel_select = QComboBox()
        self.pid_channel_select.addItem("roll_pid")
        self.pid_channel_select.addItem("pitch_pid")
        self.pid_channel_select.addItem("yaw_pid")
        self.pid_channel_select.addItem("x_pid")
        self.pid_channel_select.addItem("y_pid")
        self.pid_channel_select.addItem("z_pid")

        #Signal to change which PID controller is being tunned when selection changes
        self.pid_channel_select.currentIndexChanged.connect(self._PID_controller_change)
        self.pid_channel_select_label = QLabel("PID Controller:")
        self.pid_channel_select_label.setStyleSheet("color: black")

        #A button to save the PID values to the parameter server. This is how to sub
        #will update its PID values
        self.PID_save_values_layout = QVBoxLayout()
        self.pid_values_save = QPushButton("Save PID Values")
        self.pid_values_save.setStyleSheet("background-color:#2C878F; color:#01535B")
        self.pid_values_save.setIcon(QIcon(QPixmap("save_symbol.png")))
        self.pid_values_save.clicked.connect(self._save_pid_values)
        self.PID_save_values_layout.addWidget(self.pid_values_save, 0)

        self.PID_controller_layout.addWidget(self.pid_channel_select_label, 0, 0)
        self.PID_controller_layout.addWidget(self.pid_channel_select, 0, 1)
        self.PID_save_values_layout.addLayout(self.PID_controller_layout, 1)

        self.options_linking_layout.addLayout(self.PID_save_values_layout, 0, 1)

    def _PID_sliders(self):
        '''
        Set up the proportional, integral, and derivatives gain sliders for tunning
        the PID controls.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.slider_layout = QGridLayout()
        self.k_p_precision_layout = QGridLayout()
        self.k_i_precision_layout = QGridLayout()
        self.k_d_precision_layout = QGridLayout()

        self.k_p_slider = QSlider(Qt.Horizontal)
        self.k_p_slider.setMaximum(10)
        self.k_p_slider.setMinimum(0)
        self.k_p_slider.setValue(0)
        self.k_p_slider.valueChanged.connect(self._update_gains_with_slider)
        self.k_p_label = QLabel("K_P:")
        self.k_p_label.setStyleSheet("color: black")
        self.k_p_display = QLineEdit()
        self.k_p_display.editingFinished.connect(self._update_gain_with_line_edits)

        self.k_p_max_value_line_edit = QLineEdit()
        self.max_k_p = 10.0
        self.k_p_max_value_line_edit.setText(str(self.max_k_p))
        self.k_p_max_value_line_edit.editingFinished.connect(self._update_PID_precision)
        self.k_p_max_value_label = QLabel("Max K_P:")
        self.k_p_max_value_label.setStyleSheet("color: black")
        self.k_p_precision_combobox = QComboBox()
        self.k_p_precision_combobox.addItems(["1", "0.1", "0.01", "0.001"])
        self.precision_k_p = float(self.k_p_precision_combobox.currentText())
        self.k_p_precision_combobox.currentIndexChanged.connect(self._update_PID_precision)
        self.k_p_precision_label = QLabel("K_P Precision:")
        self.k_p_precision_label.setStyleSheet("color: black")


        self.k_i_slider = QSlider(Qt.Horizontal)
        self.k_i_slider.setMaximum(10)
        self.k_i_slider.setMinimum(0)
        self.k_i_slider.setValue(0)
        self.k_i_slider.valueChanged.connect(self._update_gains_with_slider)
        self.k_i_label = QLabel("K_I:")
        self.k_i_label.setStyleSheet("color: black")
        self.k_i_display = QLineEdit()
        self.k_i_display.editingFinished.connect(self._update_gain_with_line_edits)

        self.k_i_max_value_line_edit = QLineEdit()
        self.max_k_i = 10.0
        self.k_i_max_value_line_edit.setText(str(self.max_k_i))
        self.k_i_max_value_line_edit.editingFinished.connect(self._update_PID_precision)
        self.k_i_max_value_label = QLabel("Max K_I:")
        self.k_i_max_value_label.setStyleSheet("color: black")
        self.k_i_precision_combobox = QComboBox()
        self.k_i_precision_combobox.addItems(["1", "0.1", "0.01", "0.001"])
        self.precision_k_i = float(self.k_i_precision_combobox.currentText())
        self.k_i_precision_combobox.currentIndexChanged.connect(self._update_PID_precision)
        self.k_i_precision_label = QLabel("K_I Precision:")
        self.k_i_precision_label.setStyleSheet("color: black")

        self.k_d_slider = QSlider(Qt.Horizontal)
        self.k_d_slider.setMaximum(10)
        self.k_d_slider.setMinimum(0)
        self.k_d_slider.setValue(0)
        self.k_d_slider.valueChanged.connect(self._update_gains_with_slider)
        self.k_d_label = QLabel("K_D:")
        self.k_d_label.setStyleSheet("color: black")
        self.k_d_display = QLineEdit()
        self.k_d_display.editingFinished.connect(self._update_gain_with_line_edits)

        self.k_d_max_value_line_edit = QLineEdit()
        self.max_k_d = 10.0
        self.k_d_max_value_line_edit.setText(str(self.max_k_d))
        self.k_d_max_value_line_edit.editingFinished.connect(self._update_PID_precision)
        self.k_d_max_value_label = QLabel("Max K_D:")
        self.k_d_max_value_label.setStyleSheet("color: black")
        self.k_d_precision_combobox = QComboBox()
        self.k_d_precision_combobox.addItems(["1", "0.1", "0.01", "0.001"])
        self.precision_k_d = float(self.k_d_precision_combobox.currentText())
        self.k_d_precision_combobox.currentIndexChanged.connect(self._update_PID_precision)
        self.k_d_precision_label = QLabel("K_D Precision:")
        self.k_d_precision_label.setStyleSheet("color: black")

        self.k_p_precision_layout.addWidget(self.k_p_max_value_label, 0, 0)
        self.k_p_precision_layout.addWidget(self.k_p_max_value_line_edit, 0, 1)
        self.k_p_precision_layout.addWidget(self.k_p_precision_label, 1, 0)
        self.k_p_precision_layout.addWidget(self.k_p_precision_combobox, 1, 1)

        self.k_i_precision_layout.addWidget(self.k_i_max_value_label, 0, 0)
        self.k_i_precision_layout.addWidget(self.k_i_max_value_line_edit, 0, 1)
        self.k_i_precision_layout.addWidget(self.k_i_precision_label, 1, 0)
        self.k_i_precision_layout.addWidget(self.k_i_precision_combobox, 1, 1)

        self.k_d_precision_layout.addWidget(self.k_d_max_value_label, 0, 0)
        self.k_d_precision_layout.addWidget(self.k_d_max_value_line_edit, 0, 1)
        self.k_d_precision_layout.addWidget(self.k_d_precision_label, 1, 0)
        self.k_d_precision_layout.addWidget(self.k_d_precision_combobox, 1, 1)


        self.slider_layout.addWidget(self.k_p_label, 0, 0)
        self.slider_layout.addWidget(self.k_p_slider, 0, 1)
        self.slider_layout.addWidget(self.k_p_display, 0, 2)
        self.slider_layout.addLayout(self.k_p_precision_layout, 0, 3)

        self.slider_layout.addWidget(self.k_i_label, 1, 0)
        self.slider_layout.addWidget(self.k_i_slider, 1, 1)
        self.slider_layout.addWidget(self.k_i_display, 1, 2)
        self.slider_layout.addLayout(self.k_i_precision_layout, 1, 3)

        self.slider_layout.addWidget(self.k_d_label, 2, 0)
        self.slider_layout.addWidget(self.k_d_slider, 2, 1)
        self.slider_layout.addWidget(self.k_d_display, 2, 2)
        self.slider_layout.addLayout(self.k_d_precision_layout, 2, 3)

        self.options_linking_layout.addLayout(self.slider_layout, 0, 0)

        self._PID_controller_change()

    def _error_plotter(self):
        '''
        Initialize a real time plotter widget to display the PID error of the sub.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.error_plot = Real_Time_Plotter(title="PID Error")
        self.error_plot.add_curve("Current Error", (255, 0, 0))
        self.error_plot.add_curve("Zero Error", (0, 255, 0))
        self.primary_linking_layout.addWidget(self.error_plot, 0)


    def _update_error_plot(self, pid_error_proto):
        '''
        Update the error plot by calling the pid error subscriber. This function is
        the callback function to the pid_error_suscriber.

        Parameters:
            pid_error_proto: The pid error protobuf recieved from the pid error
                                subscriber.
        Returns:
            N/A
        '''
        self.pid_error_proto.ParseFromString(pid_error_proto)

        self.channel = self.pid_channel_select.currentIndex()

        if(self.channel == 0):
            current_error = self.pid_error_proto.roll_error
        elif(self.channel == 1):
            current_error = self.pid_error_proto.pitch_error
        elif(self.channel == 2):
            current_error = self.pid_error_proto.yaw_error
        elif(self.channel == 3):
            current_error = self.pid_error_proto.x_pos_error
        elif(self.channel == 4):
            current_error = self.pid_error_proto.y_pos_error
        elif(self.channel == 5):
            current_error = self.pid_error_proto.z_pos_error
        self.error_plot.update_values(current_error, 0)

    def _PID_controller_change(self):
        '''
        If the PID controller desired to be tune changes, this callback is called
        to position the sliders in the last set PID control position.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.channel = self.pid_channel_select.currentText()

        k_p = self.param_serv.get_param('Control/PID/' + self.channel + '/p')
        k_i = self.param_serv.get_param('Control/PID/' + self.channel + '/i')
        k_d = self.param_serv.get_param('Control/PID/' + self.channel + '/d')

        #Set the max of each channel as the value from the Parameter server

        k_p_disp = "%.3f" % (float(k_p) + 0.10*float(k_p))
        k_i_disp = "%.3f" % (float(k_i) + 0.10*float(k_i))
        k_d_disp = "%.3f" % (float(k_d) + 0.10*float(k_d))

        self.k_p_max_value_line_edit.setText(k_p_disp)
        self.k_i_max_value_line_edit.setText(k_i_disp)
        self.k_d_max_value_line_edit.setText(k_d_disp)

        #Set the precision to the max precision of the
        self.k_p_precision_combobox.setCurrentIndex(3)
        self.k_i_precision_combobox.setCurrentIndex(3)
        self.k_d_precision_combobox.setCurrentIndex(3)

        self._update_PID_precision()

        self._update_gain_displays(k_p, k_i, k_d)
        self._update_sliders(k_p, k_i, k_d)
    def _save_pid_values(self):
        '''
        This is the callback for the save pid values button. When it is pressed,
        it sets the PID gain values currently selected on the sliders/gain displays
        and writes it to the parameter server. Then it tells the navigation controller
        to update these values.

        Parameters:
            N/A

        Returns:
            N/A
        '''

        channel = self.pid_channel_select.currentText()

        #Get the current PID values seen by the sliders/gain displays. Set it
        #to the parameter server.
        k_p = self.k_p_display.text()
        k_i = self.k_i_display.text()
        k_d = self.k_d_display.text()

        self.param_serv.set_param('Control/PID/' + channel + '/p', k_p)
        self.param_serv.set_param('Control/PID/' + channel + '/i', k_i)
        self.param_serv.set_param('Control/PID/' + channel + '/d', k_d)

        time.sleep(0.01) #Make sure that the parameters are properly sent.

        #Tell the navigation controller/movement controller to update its PIDs

        self.pid_configs_update_publisher.publish(bytes('1', 'utf-8')) #The value that is sent does not matter
        print("[INFO]: Saving and Updating PID Configurations.")

    def _update_PID_precision(self):
        '''
        This function is the callback for when the desired PID gain floating point
        precision is changed. It allows for the selection of the max p, i, and d values
        for each channel.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        k_p = self.k_p_display.text()
        k_i = self.k_i_display.text()
        k_d = self.k_d_display.text()


        self.max_k_p = float(self.k_p_max_value_line_edit.text())
        self.precision_k_p = float(self.k_p_precision_combobox.currentText())
        self.k_p_slider.setMaximum(self.max_k_p * (1 / self.precision_k_p))

        self.max_k_i = float(self.k_i_max_value_line_edit.text())
        self.precision_k_i = float(self.k_i_precision_combobox.currentText())
        self.k_i_slider.setMaximum(self.max_k_i * (1 / self.precision_k_i))

        self.max_k_d = float(self.k_d_max_value_line_edit.text())
        self.precision_k_d = float(self.k_d_precision_combobox.currentText())
        self.k_d_slider.setMaximum(self.max_k_d * (1 / self.precision_k_d))

        #self._update_gain_displays(k_p, k_i, k_d)
        #self._update_sliders(k_p, k_i, k_d)

    def _update_gains_with_slider(self):
        '''
        This function is the callback called when any of the sliders change in
        value. It will update the gain displays to view what the current gain is
        via number.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        k_p = self.k_p_slider.value() * self.precision_k_p
        k_i = self.k_i_slider.value() * self.precision_k_i
        k_d = self.k_d_slider.value() * self.precision_k_d
        self._update_gain_displays(k_p, k_i, k_d)


    def _update_gain_with_line_edits(self):
        '''
        This function is the callback called when any of the gain displays change in
        value and the enter key is pressed. It will update the slider position to
        view what the current gain isvia number.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        k_p = float(self.k_p_display.text())
        if(k_p > self.max_k_p ):
            k_p = self.max_k_p
        k_i = float(self.k_i_display.text())
        if(k_i > self.max_k_i):
            k_i = self.max_k_i
        k_d = float(self.k_d_display.text())
        if(k_d > self.max_k_d):
            k_d = self.max_k_d

        self._update_sliders(k_p, k_i, k_d)
        self._update_gain_displays(k_p, k_i, k_d)


    def _update_gain_displays(self, k_p, k_i, k_d):
        '''
        Set the text for the gain displays.

        Parameters:
            k_p: The proportional gain
            k_i: Integral gain
            k_d: Derivative gain

        Returns:
            N/A
        '''
        self.k_p_display.setText(str(round(float(k_p), 3)))
        self.k_i_display.setText(str(round(float(k_i), 3)))
        self.k_d_display.setText(str(round(float(k_d), 3)))

    def _update_sliders(self, k_p, k_i, k_d):
        '''
        Set the position for the sliders.

        Parameters:
            k_p: The proportional gain
            k_i: Integral gain
            k_d: Derivative gain

        Returns:
            N/A
        '''
        self.k_p_slider.setValue(float(k_p) / self.precision_k_p)
        self.k_i_slider.setValue(float(k_i) / self.precision_k_i)
        self.k_d_slider.setValue(float(k_d) / self.precision_k_d)


if __name__ == "__main__":
    import sys
    app = QApplication([])
    pid_tuner_gui = PID_Tuner_Widget()
    app.setStyle('Fusion')
    pid_tuner_gui.show()
    sys.exit(app.exec_())
