'''
Copyright 2019, Claire Fiorino, All rights reserved
Author: Claire Fiorino<Claire Fiorino>
Last Modified 04/27/2019
Description: This PyQt widget is for capturing images to train the YOLO network
'''
import sys
import os

from image_label_widget import Image_Label

from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QColor, QPalette
from PyQt5.QtCore import QRect, QPoint, Qt

class Image_Capture(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.setGeometry(30,30,1200,900)
        
        #Make Window Transparent
        self.setWindowOpacity(0.3)

        self.begin = QPoint()
        self.end = QPoint()

        self.setLayout(layout)

        self.image_lab = Image_Label()
        self.image_lab.show()

        #FIX ME: Camera widget should be called to pop up behind the image capture widget
        #ex = Camera_Streaming()
        #ex.show()

        self.i = 0

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(1,1,0,0))  
        qp.setBrush(br)   
        qp.drawRect(QRect(self.begin, self.end))       

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()

        yfile = open("yolo_data.txt", "a")

	#Write Points to file
        point = (str)(self.begin)
	
        #Save individual values of x and y for upper left coordinate to print later
        self.point1x = self.begin.x()
        self.point1y = self.begin.y()

        #Print upper left coordinate of rectangle
        yfile.write("("+self.image_lab.cb.currentText()+") ")
        yfile.write("COORDINATES #"+(str)(self.i)+": ")
        point = " ("+(str)(self.point1x)+", "+(str)(self.point1y)+")"
        yfile.write(point)

        #FIX ME: Start qthread that takes pictures with the camera at a certain FPS rate
        #FIX ME: Set qthread flag variable to true

        #Update coordinate number
        self.i = self.i+1
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()

	#Write Points to file
        point = (str)(self.begin)
 
        #Save individual values of x and y for lower right coordinate to print later
        self.point2x = self.begin.x()
        self.point2y = self.begin.y()

        #Print lower right coordinate of rectangle
        yfile = open("yolo_data.txt", "a")
        point = " ("+(str)(self.point2x)+", "+(str)(self.point2y)+")"
        yfile.write(point)

        #Print upper right coordinate of rectangle
        point = " ("+(str)(self.point2x)+", "+(str)(self.point1y)+")"
        yfile.write(point)

        #Print lower left coordinate of rectangle
        point = " ("+(str)(self.point1x)+", "+(str)(self.point2y)+") "
        yfile.write(point)

        yfile.write("\n")

        #FIX ME: Set qthread flag variable to false, which will cause thread to stop running

        self.update()

def main():
   app = QApplication(sys.argv)
   image_cap = Image_Capture()
   image_cap.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
