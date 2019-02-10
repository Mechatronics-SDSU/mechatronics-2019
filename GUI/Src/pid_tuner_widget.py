'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 02/09/2019
Description: This PyQt widget is for tunning the PID controls.
'''
import sys
import os

PROTO_PATH = os.path.join("..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from MechOS import mechos
from protoFactory import packageProtobuf
import Mechatronics_pb2

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QCheckBox, QLabel, QSlider
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QComboBox, QPushButton
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt
import time
from real_time_plotter_widget import Real_Time_Plotter

class PID_Tuner_Widget(QWidget):
    '''
    This class is a PyQt widget for tunning the 6 degree of freedom PID control system.
    '''
    def __init__(self, pid_tuner_node):
        '''
        Initialize the layout for the widget by setting its color and instantiating its
        components:

        Parameters:
            N/A

        Returns:
            N/A
        '''
        QWidget.__init__(self)

        self.pid_tuner_node = pid_tuner_node
        self.pid_publisher = self.pid_tuner_node.create_publisher("PIDS")
        self.error_subscriber = self.pid_tuner_node.create_subscriber("PID_ERRORS", self._update_graph)

        #Mechos parameter server
        #Initialize parameter server client to get and set parameters related to sub
        self.param_serv = mechos.Parameter_Server_Client()

        parameter_xml_database = os.path.join("..", "..", "Sub", "Src", "Params", "Perseverance.xml")
        parameter_xml_database = os.path.abspath(parameter_xml_database)
        self.param_serv.use_parameter_database(parameter_xml_database)


        #Set background color of the widget
        nav_gui_palette = self.palette()
        nav_gui_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(nav_gui_palette)

        self.current_error = 0

        #Create widgets main layout structer
        self.primary_linking_layout = QVBoxLayout(self)
        self.setLayout(self.primary_linking_layout)

        self.options_linking_layout = QGridLayout()

        self._error_plotter()
        self._PID_controller_select()
        self._PID_sliders()
        self.primary_linking_layout.addLayout(self.options_linking_layout, 1)

        self.proto_decoder =  Mechatronics_pb2.Mechatronics()


    def _PID_controller_select(self):
        '''
        '''
        self.PID_controller_layout = QGridLayout()
        self.pid_channel_select = QComboBox()
        self.pid_channel_select.addItem("roll_pid")
        self.pid_channel_select.addItem("pitch_pid")
        self.pid_channel_select.addItem("yaw_pid")
        self.pid_channel_select.addItem("x_pid")
        self.pid_channel_select.addItem("y_pid")
        self.pid_channel_select.addItem("z_pid")
        self.pid_channel_select.currentIndexChanged.connect(self._PID_controller_change)
        self.pid_channel_select_label = QLabel("PID Controller:")
        self.pid_channel_select_label.setStyleSheet("color: white")

        self.PID_save_values_layout = QVBoxLayout()
        self.pid_values_save = QPushButton("Save PID Values")
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
        self.k_p_label.setStyleSheet("color: white")
        self.k_p_display = QLineEdit()
        self.k_p_display.editingFinished.connect(self._update_gain_with_line_edits)

        self.k_p_max_value_line_edit = QLineEdit()
        self.max_k_p = 10.0
        self.k_p_max_value_line_edit.setText(str(self.max_k_p))
        self.k_p_max_value_line_edit.editingFinished.connect(self._update_PID_precision)
        self.k_p_max_value_label = QLabel("Max K_P:")
        self.k_p_max_value_label.setStyleSheet("color: white")
        self.k_p_precision_combobox = QComboBox()
        self.k_p_precision_combobox.addItems(["1", "0.1", "0.01", "0.001"])
        self.precision_k_p = float(self.k_p_precision_combobox.currentText())
        self.k_p_precision_combobox.currentIndexChanged.connect(self._update_PID_precision)
        self.k_p_precision_label = QLabel("K_P Precision:")
        self.k_p_precision_label.setStyleSheet("color: white")


        self.k_i_slider = QSlider(Qt.Horizontal)
        self.k_i_slider.setMaximum(10)
        self.k_i_slider.setMinimum(0)
        self.k_i_slider.setValue(0)
        self.k_i_slider.valueChanged.connect(self._update_gains_with_slider)
        self.k_i_label = QLabel("K_I:")
        self.k_i_label.setStyleSheet("color: white")
        self.k_i_display = QLineEdit()
        self.k_i_display.editingFinished.connect(self._update_gain_with_line_edits)

        self.k_i_max_value_line_edit = QLineEdit()
        self.max_k_i = 10.0
        self.k_i_max_value_line_edit.setText(str(self.max_k_i))
        self.k_i_max_value_line_edit.editingFinished.connect(self._update_PID_precision)
        self.k_i_max_value_label = QLabel("Max K_I:")
        self.k_i_max_value_label.setStyleSheet("color: white")
        self.k_i_precision_combobox = QComboBox()
        self.k_i_precision_combobox.addItems(["1", "0.1", "0.01", "0.001"])
        self.precision_k_i = float(self.k_i_precision_combobox.currentText())
        self.k_i_precision_combobox.currentIndexChanged.connect(self._update_PID_precision)
        self.k_i_precision_label = QLabel("K_I Precision:")
        self.k_i_precision_label.setStyleSheet("color: white")

        self.k_d_slider = QSlider(Qt.Horizontal)
        self.k_d_slider.setMaximum(10)
        self.k_d_slider.setMinimum(0)
        self.k_d_slider.setValue(0)
        self.k_d_slider.valueChanged.connect(self._update_gains_with_slider)
        self.k_d_label = QLabel("K_D:")
        self.k_d_label.setStyleSheet("color: white")
        self.k_d_display = QLineEdit()
        self.k_d_display.editingFinished.connect(self._update_gain_with_line_edits)

        self.k_d_max_value_line_edit = QLineEdit()
        self.max_k_d = 10.0
        self.k_d_max_value_line_edit.setText(str(self.max_k_d))
        self.k_d_max_value_line_edit.editingFinished.connect(self._update_PID_precision)
        self.k_d_max_value_label = QLabel("Max K_D:")
        self.k_d_max_value_label.setStyleSheet("color: white")
        self.k_d_precision_combobox = QComboBox()
        self.k_d_precision_combobox.addItems(["1", "0.1", "0.01", "0.001"])
        self.precision_k_d = float(self.k_d_precision_combobox.currentText())
        self.k_d_precision_combobox.currentIndexChanged.connect(self._update_PID_precision)
        self.k_d_precision_label = QLabel("K_D Precision:")
        self.k_d_precision_label.setStyleSheet("color: white")

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

        #self._update_PID_precision()
        self._PID_controller_change()

    def _error_plotter(self):
        '''
        '''
        self.error_plot = Real_Time_Plotter(title="PID Error")
        self.error_plot.add_curve("Current Error", (255, 0, 0))
        self.error_plot.add_curve("Zero Error", (0, 255, 0))
        self.primary_linking_layout.addWidget(self.error_plot, 0)


    def _update_graph(self, pid_error_proto):
        '''
        '''
        self.proto_decoder.ParseFromString(pid_error_proto)

        self.channel = self.pid_channel_select.currentIndex()
        if(self.channel == 0):
            current_error = self.proto_decoder.pid_error.roll_error
        elif(self.channel == 1):
            current_error = self.proto_decoder.pid_error.pitch_error
        elif(self.channel == 2):
            current_error = self.proto_decoder.pid_error.yaw_error
        elif(self.channel == 3):
            current_error = self.proto_decoder.pid_error.x_error
        elif(self.channel == 4):
            current_error = self.proto_decoder.pid_error.y_error
        elif(self.channel == 5):
            current_error = self.proto_decoder.pid_error.z_error
        self.error_plot.update_values(current_error, 0)

    def _PID_controller_change(self):
        '''
        '''
        self.channel = self.pid_channel_select.currentText()

        k_p = self.param_serv.get_param('Control/PID/' + self.channel + '/p')
        k_i = self.param_serv.get_param('Control/PID/' + self.channel + '/i')
        k_d = self.param_serv.get_param('Control/PID/' + self.channel + '/d')

        self._update_gain_displays(k_p, k_i, k_d)
        self._update_sliders(k_p, k_i, k_d)

    def _save_pid_values(self):

        channel = self.pid_channel_select.currentText()
        k_p = self.k_p_display.text()
        k_i = self.k_i_display.text()
        k_d = self.k_d_display.text()

        self.param_serv.set_param('Control/PID/' + channel + '/p', k_p)
        self.param_serv.set_param('Control/PID/' + channel + '/i', k_i)
        self.param_serv.set_param('Control/PID/' + channel + '/d', k_d)

    def _update_PID_precision(self):

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

        self._update_gain_displays(k_p, k_i, k_d)
        self._update_sliders(k_p, k_i, k_d)

    def _update_gains_with_slider(self):

        k_p = self.k_p_slider.value() * self.precision_k_p
        k_i = self.k_i_slider.value() * self.precision_k_i
        k_d = self.k_d_slider.value() * self.precision_k_d
        self._update_gain_displays(k_p, k_i, k_d)
        self._publish_pid_values(k_p, k_i, k_d)


    def _update_gain_with_line_edits(self):
        '''
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
        self._publish_pid_values(k_p, k_i, k_d)

    def _update_gain_displays(self, k_p, k_i, k_d):
        self.k_p_display.setText(str(round(float(k_p), 3)))
        self.k_i_display.setText(str(round(float(k_i), 3)))
        self.k_d_display.setText(str(round(float(k_d), 3)))

    def _update_sliders(self, k_p, k_i, k_d):
        self.k_p_slider.setValue(float(k_p) / self.precision_k_p)
        self.k_i_slider.setValue(float(k_i) / self.precision_k_i)
        self.k_d_slider.setValue(float(k_d) / self.precision_k_d)

    def _publish_pid_values(self, k_p, k_i, k_d):
        '''
        '''
        pid_values = [0, 0, 0, 0]
        pid_values[0] = self.pid_channel_select.currentIndex()
        pid_values[1] = k_p
        pid_values[2] = k_i
        pid_values[3] = k_d

        pid_proto = packageProtobuf("PIDS", pid_values)
        pid_proto_serialized = pid_proto.SerializeToString()
        self.pid_publisher.publish(pid_proto_serialized)

if __name__ == "__main__":
    import sys
    app = QApplication([])
    pid_tuner_gui = PID_Tuner_Widget()
    app.setStyle('Fusion')
    pid_tuner_gui.show()
    sys.exit(app.exec_())
