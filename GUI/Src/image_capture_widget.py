'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino<Claire Fiorino>
Last Modified 04/27/2019
Description: This PyQt widget is for capturing images to train the YOLO network. It consists of a drop-down menu where you can select the object you want to identify, and a transparent window (that is supposed to pop up in front of a camera stream) where you can click and draw rectangles around those objects.
'''
import sys
import os

from image_label_widget import Image_Label
from webcam_thread import Webcam_Thread

from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QColor, QPalette, QPen
from PyQt5.QtCore import QRect, QPoint, Qt

class Image_Capture(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout()

        self.setGeometry(30,30,2000,1500)
        
        #Make Window Transparent
        self.setWindowOpacity(0.3)

        self.begin = QPoint()
        self.end = QPoint()

        self.setLayout(layout)

        self.image_lab = Image_Label()
        self.image_lab.show()

        #FIXME: Camera stream widget should be called to pop up behind the image capture widget

        #START WEBCAM THREAD
        self.web_thread = Webcam_Thread()
        self.web_thread.start()
        self.web_thread.threadrunning = True

    def paintEvent(self, event):

        qp = QPainter(self) 

        if self.image_lab.cb.currentIndex() == 0:
            qp.setPen(QPen(Qt.blue, 10))
        elif self.image_lab.cb.currentIndex() == 1:
            qp.setPen(QPen(Qt.red, 10))
        elif self.image_lab.cb.currentIndex() == 2:
            qp.setPen(QPen(Qt.yellow, 10))
        elif self.image_lab.cb.currentIndex() == 3: 
            qp.setPen(QPen(Qt.green, 10))

        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):

        self.begin = event.pos()
        self.end = event.pos()
	
        #Save individual values of x and y for upper left coordinate to print later
        global point1x
        point1x = self.begin.x()

        global point1y
        point1y = self.begin.y()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):

        self.begin = event.pos()
        self.end = event.pos()

        name = "img"+(str)(self.web_thread.imageNumber)+".txt"
        yfile = open(name, "a")

        #Print index of object being identified followed by space
        yfile.write((str)(self.image_lab.cb.currentIndex())+" ")
 
        #Save individual values of x and y for lower right coordinate to print later
        self.point2x = self.end.x()
        self.point2y = self.end.y()

        #Print x value of coordinate at center of rectangle followed by space
        middlex = (self.point2x-point1x)/2
        yfile.write((str)(1/middlex)+" ")

        #Print y value of coordinate at center of rectangle followed by space
        middley = (self.point2y-point1y)/2
        yfile.write((str)(1/middley)+" ")

        #Print width of rectangle followed by space
        width = self.point2x-point1x
        yfile.write((str)(1/width)+" ")

        #Print height of rectangle followed by space
        height = self.point2x-point1x
        yfile.write((str)(1/width)+" ")

        yfile.write("\n")

        self.update()

def main():
   app = QApplication(sys.argv)
   image_cap = Image_Capture()
   image_cap.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
