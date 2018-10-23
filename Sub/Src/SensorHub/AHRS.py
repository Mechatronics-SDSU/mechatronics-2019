'''
Copyright 2018, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell
Last Modified 10/23/2018
Description: This module is the driver program for the Sparton AHRS.
'''
from sensorHub import SensorHubBase

class SpartonAHRSDataPackets:
    '''
    This class implements the getters and setters commands for the Sparton AHRS.
    It handles the sending values to configure the device and request data specified
    data.
    '''
    def __init__(self, com_port):
        '''
        Initializes connection with the AHRS device at a baud rate of 115200.
        Sets up the array of location values.

        Parameters:
            com_port: A string value of the serial COM port that the AHRS
                            device is connected to.
        Returns:
            N/A
        '''

        self.ahrs = serial.Serial(com_port, 115200)
        self.locationArray = [[0x01, 9], [0x02, 5], [0x09, 5], [0x83, 5],
        [0x0F, 5], [0x8B, 5], [0x8C, 5], [0x8D, 5], [0x8E, 5], [0x04, 11],
        [0x56, 4], [0x08, 5], [0x05, 9], [0x06, 7], [0x07, 11], [0x11, 5],
        [0x57, 4], [0x4A, 4]]

class AHRS(SensorHubBase):

    def __init__(self):
        super(AHRS, self).__init__()
        #Change type to match protobuf type
        self.type = "AHRS_DATA"
        #Establish connection with sensor

    #TODO
    def receiveData(self):
        pass

if __name__ == "__main__":
    ahrs = AHRS()
    print(ahrs.type)
