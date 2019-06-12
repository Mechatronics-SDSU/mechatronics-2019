import serial
import struct
class maestro(object):
    def __init__(self, path='/dev/ttyACM0', baud=9600):
        Initialization="""
        {} Object initialized:
        PORT:{}
        BAUD:{}
        """.format(__class__.__name__, path, baud)
        print(Initialization)
        self.serialStream=serial.Serial(path, baud)

    def set_target(self, thrusterID, thrust):
        self.serialStream.write(bytearray([0xFF, thrusterID, thrust]))
