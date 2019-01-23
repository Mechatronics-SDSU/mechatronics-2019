'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 01/14/2019
Description: This module is the driver program for the backplane. It is responsible for
receiving all the sensor data and sending the actuator data for devices connected to
the backplane.
'''

import sys
import os
HELPERS_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPERS_PATH)
PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from MechOS import mechos
from sensorHub import SensorHubBase
import serial
import time
import struct
from protoFactory import packageProtobuf
import Mechatronics_pb2
import threading
from pressureTransducers import Pressure_Depth_Transducers


class Backplane_Requests():
    '''
    Responsible for requesting data or sending actions to the backplane for
    various sensors and actuators such as pressure transducers and weapon controls.
    '''

    def __init__(self, backplane_serial_obj):
        '''
        Initializes connection with the backplane through serial communication.

        Parameters:
            backplane_serial_obj: An already initialized serial communication object
                                to the backplane.
        Returns:
            N/A
        '''
        self.backplane_serial = backplane_serial_obj
        self.header_byte = 0xEE #header byte expected by backplane
        self.termination_byte = 0x50 #termination byte expected by backplane


    def request_pressure_transducer_data(self):
        '''
        Request pressure data from transducers.

        Note: The request for pressure data is given by
            byte_1: self.header_byte
            byte_2: 0x41
            byte_3: self.termination_byte

        Parameters:
            N/A

        Returns:
            true: If request for transducer data is successful
            false: If request for transducer data is unsuccessful
        '''
        data_packet = bytearray([self.header_byte, 0x41, 0x70])

        try:
            self.backplane_serial.write(data_packet)
            return True
        except Exception as e:
            print("Could not request pressure transducer data from backplane:", e)
            return False



class Backplane_Responses(threading.Thread):
    '''
    The class is a thread that reads all the responses from the backplane continously.
    '''
    def __init__(self, backplane_serial_obj):
        '''
        Initialize the backplane response thread to connect through serial to
        backplane.

        Parameters:
            backplane_serial_obj: An already initialized serial communication object
                                to the backplane.

        Returns:
            N/A
        '''

        threading.Thread.__init__(self)

        self.backplane_serial = backplane_serial_obj

        self.header_byte = 0xEE

        self.run_thread = True
        self.daemon = True

        #A list(Queue) to store data received from backplane
        self.backplane_data = []

    def run(self):
        '''
        Run the tread to continually receive data from the backplane and store
        in backplane_data queue.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while self.run_thread:

            backplane_data_packet = self._unpack()

            if backplane_data_packet != None:
                self.backplane_data.append(backplane_data_packet)
            time.sleep(0.1)
    def _unpack(self):
        '''
        Read in the transmission from the backplane and extract the data from it

        Parameter:
            N/A

        Returns:
            N/A
        '''
        try:
            if self.backplane_serial.in_waiting > 0:


                #read in first byte and check if it is the correct header byte
                #header byte should be 0xEE
                header_byte = ord(self.backplane_serial.read())
                if header_byte == self.header_byte:

                    byte_1 = ord(self.backplane_serial.read())
                    byte_2 = ord(self.backplane_serial.read())

                    id_frame = (struct.unpack('h', struct.pack('H', (byte_1 << 3) | (byte_2 >> 5)))[0])

                    rtr = (struct.unpack('b', struct.pack('B', 0x01 & (byte_2 >> 4)))[0])

                    #number of bytes to read for incoming data
                    payload_length = (struct.unpack('b', struct.pack('B', 0x0F & byte_2))[0])

                    payload = []

                    #read in the data being carried by data packet. Note not all carry data
                    if payload_length > 0:
                        for idx in range(payload_length):
                            payload.append(ord(self.backplane_serial.read()))

                    if id_frame == 8:   #Kill Switch Interrupt
                        message = {"KS": 0}
                        print("**KILL SWITCH INTERRUPT**")
                    elif id_frame == 16:    #Leak Interrupt
                        message = {"LI": 0}
                        print("**LEAK INTERRUPT")
                    elif id_frame == 24:    #Depth interrupt
                        message = {"DI": 0}
                        print("**DEPTH INTERRUPT**")
                    elif id_frame == 32:    #SIB Interrupt
                        message = {"SIBI": 0}
                        print("**SIB INTERRUPT")
                    elif id_frame == 104:   #Backplane Current Interrupt
                        current = payload[0]
                        message = {"BPCurrent": current}
                        print("**BACKPLANE CURRENT INTERRUPT")
                    elif id_frame == 112:   #AUTONOMOUS MODE
                        message = {"AM": 0}
                        print("**AUTONOMOUS MODE**")
                    elif id_frame == 224: #Weapon 1 on
                        message = {"W1": 0}
                        print("**WEAPON 1 ON")
                    elif id_frame == 232:# Weapon 2 on
                        message = {"W2": 0}
                        print("**WEAPON 2 ON")
                    elif id_frame == 240:# Weapon 3 on
                        message = {"W3": 0}
                        print("**WEAPON 3 ON")
                    elif id_frame == 248:# Weapon 4 on
                        message = {"W4": 0}
                        print("**WEAPON 4 ON")
                    elif id_frame == 256:# Weapon 5 on
                        message = {"W5": 0}
                        print("**WEAPON 5 ON")
                    elif id_frame == 264:# Weapon 6 on
                        message = {"W6": 0}
                        print("**WEAPON 6 ON")
                    elif id_frame == 272:# Weapon 7 on
                        message = {"W7": 0}
                        print("**WEAPON 7 ON")
                    elif id_frame == 280:# Weapon 8 on
                        message = {"W8": 0}
                        print("**WEAPON 8 ON")
                    elif id_frame == 288:# Weapon 9 on
                        message = {"W9": 0}
                        print("**WEAPON 9 ON")
                    elif id_frame == 296:# Weapon 10 on
                        message = {"W10": 0}
                        print("**WEAPON 10 ON")
                    elif id_frame == 304:# Weapon 11 on
                        message = {"W11": 0}
                        print("**WEAPON 11 ON")
                    elif id_frame == 312:# Weapon 12 on
                        message = {"W12": 0}
                        print("**WEAPON 12 ON")
                    elif id_frame == 320:# Weapon 13 on
                        message = {"W13": 0}
                        print("**WEAPON 13 ON")
                    elif id_frame == 392:   #Read in pressure data from the three pressure sensors
                        #Byte 2 (bits 0-1) shifted 8 bits left OR Byte 1 (bits 0-7)
                         ext_pressure_1 = struct.unpack('H', struct.pack('H', (payload[1] & int('0x03', 0)) << 8 | payload[0]))[0]
                         #Byte 3 (bits 0-3) shifted 6 bits left OR Byte 2 (bits 2-7) shifted 2 bits right
                         ext_pressure_2 = struct.unpack('H', struct.pack('H', (payload[2] & int('0xF', 0)) << 6 | payload[1] >> 2))[0]
                         #Byte 4 (bits 0-5) shifted 4 bits left OR Byte 3 (bits 4-7) shifted 4
                         ext_pressure_3 = struct.unpack('H', struct.pack('H', (payload[3] & int('0x1F', 0)) << 4 | payload[2] >> 4))[0]
                         inter_pressure_1 = (struct.unpack('i', struct.pack('I', payload[4] | payload[5] << 8 | (int('0xF', 0) & payload[6]) << 16))[0])
                         #message = {"Press":[ext_pressure_1,ext_pressure_2, ext_pressure_3, inter_pressure_1]}

                         #Currently only these two transducers are operational
                         message = {"Press":[ext_pressure_2, ext_pressure_3]}
                    elif id_frame == 400:   #This use to be used for an internal pressure sensor
                        pass

                    elif id_frame == 656:
                        message = {"BMS": 0}
                        print("**GOT BMS START MESSAGE**")
                    elif id_framw == 648:   #voltage data
                        voltage = float(payload[0]) + (float(payload[1]) / 100)
                        message = {"Voltage": voltage}

                    self.backplane_serial.flushInput()
                    return message

        except Exception as e:
            print("Can't receive data from backplane:", e)

class Backplane_Handler():
    '''
    This class handles requests and responses to the backplane and publishs any
    necessary received data to the MechOS network.
    '''

    def __init__(self, com_port):
        '''
        Initialize serial connection to the backplane, start the backplane response
        thread.

        Parameters:
            com_port: The serial communication port that the backplane is connected
                        to.
        Returns:
            N/A
        '''

        backplane_serial_obj = serial.Serial(com_port, 9600)

        #Initialize object request for data to the backplane
        self.backplane_requests = Backplane_Requests(backplane_serial_obj)

        #Initialize thread object for queuing up data received from backplane
        self.backplane_response_thread = Backplane_Responses(backplane_serial_obj)

        #Initialize pressure transducer thread
        self.depth_transducers_thread = Pressure_Depth_Transducers(backplane_serial_obj)

        #start backplane response thread
        self.backplane_response_thread.start()
        self.depth_transducers_thread.start()


    def run(self):
        '''
        Continually receive data from the backplane and perform any necessary
        processing of that data.

        Parameters:
            N/A

        Returns:
            N/A
        '''

        while(1):

            try:
                #Make request for data
                self.backplane_requests.request_pressure_transducer_data()

                if(len(self.backplane_response_thread.backplane_data) != 0):
                #pop off data from the backplane
                    backplane_data = self.backplane_response_thread.backplane_data.pop(0)
                    if "Press" in backplane_data.keys():
                        self.depth_transducers_thread.raw_pressure_data.append(
                                                        backplane_data["Press"])
            except Exception as e:
                print("Cannot pop backplane data:", e)

        


if __name__ == "__main__":
    backplane_handler = Backplane_Handler("COM6")
    backplane_handler.run()
