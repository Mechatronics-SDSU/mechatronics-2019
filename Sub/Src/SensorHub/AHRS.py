'''
Copyright 2018, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 11/4/2018
Description: This module is the driver program for the Sparton AHRS.
'''
from sensorHub import SensorHubBase
import serial

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

        self.ahrs_serial = serial.Serial(com_port, 115200)
        self.success_header_byte = 0xA4
        self.error_header_byte = 0xAE
        self.termination_byte = 0xA0

        #Refer to page 38-43 for more information about locationarray
        self.location_array = {"raw_magnetics":[0x01, 9], "true_heading":[0x02, 5],
        "magnetic_heading":[0x09, 5], "magnetic_variation":[0x83, 5],
        "auto_magnetic_variation":[0x0F, 5], "latitude":[0x8B, 5],
        "longitude":[0x8C, 5], "altitude":[0x8D, 5], "day":[0x8E, 5],
        "magnetic_vector":[0x04, 11], "raw_acceleration":[0x05, 9],
        "pitch_roll_output":[0x06, 7], "accleration_vector":[0x07, 11],
        "temperature":[0x11, 5], "baud_rate":[0x57, 4],
        "mounting_config":[0x4A, 4]}

    def get_raw_magnetics(self):
        '''
        Send request to get the raw magnetics from the magnetometers (Mx, My,
        and Mz). These are raw sensor readings and do not yet have any
        calibration.

        Reference: Software-Interface-Manual page 38

         Send: 3 Byte (0xA4,0x01,0xA0)

        Response: 9 Bytes (0xA4,0x01,<Mx>,<My>,<Mz as 16-bit integers MS
         byte first>,0xA0)

         Parameters:
            N/A
        Returns:
            N/A
        '''
        self.sparton_ahrs_serial.write([0xA4, 0x01, 0xA0])
        return self._unpack("raw_magnetics")

    def _unpack(self, data_type):
        '''
        Read in the transmission from AHRS and extract all the byts of the
        packet.

        Parameters:
            datatype: The type of data being read. Note: This should be one of
                    the keys in the locationArray
        Returns:
            ahrs_data_in: The raw data packet of the given data type. If there is
                        an error reading the data, return None. If there are no
                        datapacket to be read, return an empty list of data.
        '''
        #Read incoming data bytes
        ahrs_data_in = []

        if self.ahrs_serial.in_waiting > 0:

            #Read in header byte
            header_byte = ord(self.ahrs_serial.read())

            #successful header byte
            if header_byte == self.success_header_byte:

                #Read second byte to confirm successful packet
                type_byte = ord(self.ahrs_serial.read())
                if type_byte == self.location_array[data_type][0]:
                    #read the given number of data bytes specified by location array
                    for idx in range(0, self.location_array[data_type][1] - 2):
                        ahrs_data_in.append(ord(self.ahrs_serial.read()))

                    #confirm correct termination of data packet
                    if ahrs_data_in[-1] != self.termination_byte:
                        return None

            #error header byte
            elif header_byte == self.error_header_byte:
                return None
        #Note: Don't include the header or termination bytes in the raw data
        return ahrs_data_in[:-1]


class AHRS(SensorHubBase):
    '''
    Communicate with the AHRS module and receive the necessary data need for
    autonomy. Publish data to sensor hub to be routed to the mission planner and
    movement control.
    '''
    def __init__(self, com_port):
        '''
        Initialize communcication path with the Sparton AHRS.

        Parameters:
            com_port: The serial communication port communicating with the AHRS
                        board.
        '''
        super(AHRS, self).__init__()
        #Change type to match protobuf type
        self.type = "AHRS_DATA"
        self.com_port = com_port

        #create object for Sparton AHRS data packets
        self.sparton_ahrs = SpartonAHRSDataPackets(com_port)

    def run(self):
        '''
        Continually request data from the AHRS merger board and publish it to
        MechOS network over topic "AHRS_DATA".

        Parameters:
            N/A

        Returns:
            N/A
        '''
        try:
            while(1):
                pass
        except:
            print("AHRS communication shutting down")

if __name__ == "__main__":
    ahrs = AHRS()
    print(ahrs.type)
