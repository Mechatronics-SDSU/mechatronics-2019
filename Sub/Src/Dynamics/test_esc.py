'''
Author: David Pierce Walker-Howell
Date: 07/05/2019
Description: Quick and Dirty script made to test a single thruster on
            thruster id 1. This was used to test the esc's when the sub
            flooded. Worked well.
'''
import serial
from thruster import Thruster
import time

ser = serial.Serial("/dev/ttyACM0", 9600)
thruster_1 = Thruster(ser, 1, [0, 0, 0], [0, 0, 0], 40)
thruster_1.set_thrust(20)
time.sleep(2)
thruster_1.set_thrust(0)

