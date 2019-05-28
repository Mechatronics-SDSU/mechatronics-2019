'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino<Claire Fiorino>
Last Modified 04/27/2019
Description: This PyQt widget is for labeling images to train the YOLO network
'''

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QComboBox

class Image_Label(QWidget):
   def __init__(self, parent = None):
      super(Image_Label, self).__init__(parent)
      
      layout = QHBoxLayout()
      self.cb = QComboBox()
      self.cb.addItems(["Right Post", "Left Post", "Buoy", "Target"])

      self.setGeometry(30,30,200,200)

      #Line up image capture widget with image label widget
      self.move(1300,0)

      layout.addWidget(self.cb)
      self.setLayout(layout)

		
def main():
   app = QApplication(sys.argv)
   ex = Image_Label()
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()

