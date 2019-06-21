'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/08/2019
Description: This module is a PyQt5 widget for plotting real time data/
'''
import pyqtgraph as pg
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import random
import time
import math

class Real_Time_Plotter(QtWidgets.QWidget):
	'''
	The Real Time Plotter class is a PyQt 5 widget based of of pyqtgraph for dynamic
	data plotting in real time. Multiple dynamic curves can be plotted simultaneous
	against one another.
	'''
	def __init__(self, time_window=10, sample_time_int=1, title="Real Time Plotter", dim=[600, 250]):
		'''
		Initialize the plotting graph time window and data buffer_sizes corresponding
		to the sampling time.

		Parameter:
			time_window: The width of the dynamic plot to view.
			sample_time_int: The period of time points (samples) to be plotted.
			title: The title for the entire graph.

		Returns:
			N/A
		'''
		#Initialize super class as a PyQt5 widget
		QtWidgets.QWidget.__init__(self)

		self.title = title

		#List to store all the curves to be plotted
		self.curves = None

		#The x-axis time frame to show data(if time_window = 10, then you will see 10 seconds of data plots)
		self.time_window = time_window
		self.sample_time_int = sample_time_int 	#Update rate of graph

		#Size of sensor data array that will be updated and plotted at each time sample
		self.buffer_size = time_window/sample_time_int

		#Evenly scaled matrix to plot sensor data against
		self.x_axis_time_frame = np.linspace(0, 10, self.buffer_size)

		#Initialize the PlotWidget(the widget to be added into the Qt Gui)
		self.plt = pg.PlotWidget(title=self.title)
		
		self.plt.resize(dim[0], dim[1])	#size: 600x250
		self.plt.showGrid(x=True, y=True)
		self.plt.setLabel('left', 'Data')
		self.plt.setLabel('bottom', 'Time')

		#Add a Legend for the data
		self.plt.addLegend()

		#initialize a single curve to be plotted
		self.y_axis_default_data = np.ones(int(self.buffer_size), dtype=np.float)

		layout = QtWidgets.QVBoxLayout(self)
		layout.addWidget(self.plt)

	def add_curve(self, curve_title, curve_color):
		'''
		Add a new curve to be dynamically plotted.

		Parameters:
			curve_title: The title of the curve
			curve_color: The RGB color for the curve. Provide as a tuple/list
						with each color range being 0-255.

						Example: Red -> (255, 0, 0). Blue -> (0, 0, 255)
		Returns:
			N/A
		'''
		if(self.curves is None):
			self.curves = {}
			self.curves_y_data = {}

		color = pg.mkPen(color=curve_color)
		self.curves[curve_title] = self.plt.plot(self.x_axis_time_frame,
								self.y_axis_default_data, pen=color, name=curve_title)
		self.curves_y_data[curve_title] = self.y_axis_default_data

	def update_values(self, *data_points):
		'''
		Update each curve with a new data point. Only one data point for each graph
		should be given

		Parameters:
			*data_points: Dynamically pass a data point for each curve in the order
							the curves were added. Note that the number of data_point
							parameters must be equivalent to the number of curves

		Returns:
			N/A
		'''


		for index, curve in enumerate(self.curves.keys()):
			self.curves_y_data[curve] = (np.append(self.curves_y_data[curve],
									data_points[index]))[1:]
			self.curves[curve].setData(self.x_axis_time_frame, self.curves_y_data[curve])
