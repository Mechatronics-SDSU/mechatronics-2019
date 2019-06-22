'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified: 06/22/2019
Description: This module is the driver program for the Sparton AHRS.
'''
import sys
import os

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

import serial
import time
import struct
import threading
from MechOS import mechos


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
        "pitch_roll":[0x06, 7], "accleration_vector":[0x07, 11],
        "temperature":[0x11, 5], "baud_rate":[0x57, 4],
        "mounting_config":[0x4A, 4]}

    def get_raw_magnetics(self):
        '''
        Send request to get the raw magnetics from the magnetometers (Mx, My,
        and Mz). These are raw sensor readings and do not yet have any
        calibration. Note that this function is really only used for test purposes.
        NOT PRACTICAL FOR OFFICIAL USE.

        Reference: Software-Interface-Manual page 38

         Send: 3 Byte (0xA4,0x01,0xA0)

        Response: 9 Bytes (0xA4,0x01,<Mx>,<My>,<Mz as 16-bit integers MS
         byte first>,0xA0)

         Parameters:
            N/A
        Returns:
            raw_magnetics: 6-byte list of raw magnetics.
        '''
        self.ahrs_serial.write(bytearray([0xA4, 0x01, 0xA0]))
        return self._unpack("raw_magnetics")

    def get_true_heading(self):
        '''
        Send request to get the true heading. True heading is the magnetic
        heading.

        Reference: Software-Interface-Manual page 38.

        Send: 3 Bytes (0xA4, 0x02, 0xA0)

        Responds: 5 Bytes <0xA4, 0x02, <Heading as a 16-bit signed integer>,
                            0xA0)
        Heading (degrees) = 16-bit Heading value * (360/4096)
        Heading Range = 0.0 to + 359.9

        Returns:
            true_heading: The true heading in degrees from 0.0 to 359.9. If the
                            data could not be received, return an empty list.
        '''
        self.ahrs_serial.write(bytearray([0xA4, 0x02, 0xA0]))
        true_heading = self._unpack("true_heading")

        if(len(true_heading) == 2):
            #convert the raw true heading data into degree
            true_heading = struct.pack('H', (true_heading[0]<<8) | (true_heading[1]))
            true_heading = struct.unpack('h', true_heading)[0]*(360.0/4096.0)
            return true_heading
        return [None]

    def get_pitch_roll(self):
        '''
        Send request and receive data to get the pitch and roll of the platform.

        Reference: Sofware-Inference-Manual page 42.

        Send: 3 Bytes (0xA4, 0x06, 0xA0)

        Response: 7 Bytes (0xA4, 0x06, Pitch, Roll as 16-bit signed integers, 0xA0)

        Pitch(in degrees) = (Response) * 90/4096
        Pitch Range: -90 to +90

        Roll (in degrees) = (Response) * 180/4096
        Acceleration Vector Roll Range = -180 to 180

        Returns:
            pitch_roll: A list containing the pitch and roll
        '''
        self.ahrs_serial.write(bytearray([0xA4, 0x06, 0xA0]))
        pitch_roll = self._unpack("pitch_roll")


        if(len(pitch_roll) == 4):
            #structs are used to make pitch signed
            pitch = struct.pack('H', (pitch_roll[0] << 8) | pitch_roll[1])
            pitch = struct.unpack('h', pitch)[0] * (90.0/4096.0)

            roll = struct.pack('H', (pitch_roll[2] << 8) | pitch_roll[3])
            roll = struct.unpack('h', roll)[0] * (180.0/4096.0)
            return [pitch, roll]
        return [None, None]

    def _unpack(self, data_type):
        '''
        Read in the transmission from AHRS and extract all the bytes of the
        packet.

        Parameters:
            datatype: The type of data being read. Note: This should be one of
                    the keys in the locationArray(see constructor)
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


class AHRS(threading.Thread):
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

        #serial communication port of the AHRS.
        self.ahrs_com_port = com_port

        #create object for Sparton AHRS data packets
        self.sparton_ahrs = SpartonAHRSDataPackets(com_port)

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        #Initialize a timer for consistent timing on data
        self.ahrs_timer_interval = float(self.param_serv.get_param("Timing/AHRS"))
        self.ahrs_timer = util_timer.Timer()

        self.threading_lock = threading.Lock()
        self.run_thread = True
        self.daemon = True

        self.ahrs_data = [0, 0, 0] #roll, pitch, yaw

    def receive_sensor_data(self):
        '''
        Receive the AHRS roll, pitch, and yaw data from the sparton ahrs module.

        Parameters:
            N/A

        Returns:
            [yaw, pitch, roll]: List of roll, pitch, yaw data. This is only returned
                    if the data is received properly.

            False: If data is not recieved properly, return false
        '''
        #Get roll, pitch, and yaw data from sparton ahrs module
        yaw = self.sparton_ahrs.get_true_heading()
        pitch, roll = self.sparton_ahrs.get_pitch_roll()

        if(yaw != None and pitch != None and roll != None):
            return [roll, pitch, yaw]
        else:
            #return false if some or all the data was received incorrectly
            return False

    def run(self):
        '''
        Continually request data from the AHRS merger board and publish it to
        MechOS network over topic "AHRS_DATA".

        Parameters:
            N/A

        Returns:
            N/A
        '''

        self.ahrs_timer.restart_timer()

        while(self.run_thread):

            try:
                ahrs_time = self.ahrs_timer.net_timer()

                #Wait necessary amont of time berof receiving and publihsing data
                if(ahrs_time < self.ahrs_timer_interval):
                    time.sleep(self.ahrs_timer_interval - ahrs_time)
                    self.ahrs_timer.restart_timer()
                else:
                    self.ahrs_timer.restart_timer()

                data = self.receive_sensor_data()

                if(data is not False):

                    #set ahrs data variable to be able to share data across threads
                    with self.threading_lock:

                        self.ahrs_data = data
            except Exception as e:
                print("[ERROR]: Couldn't receive and store AHRS data correctly. Error:", e)



if __name__ == "__main__":

    #Get the mechos network parameters
    configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

    param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
    parameter_xml_database = os.path.join("..", "Params", "Perseverance.xml")
    parameter_xml_database = os.path.abspath(parameter_xml_database)
    param_serv.use_parameter_database(parameter_xml_database)

    com_port = param_serv.get_param("COM_Ports/AHRS")
    ahrs = AHRS(com_port)
    ahrs.run()
