'''
Copyright 2018, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 12/22/2018
Description: This module is the driver of the pressure transducers on the sub
                used for determining depth.
'''
import sys
import os
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

class Pressure_Transducer:
    '''
    The Pressure transducer class is used to communicate with the pressure
    transducers on the sub via serial. The data packets received from a
    transducer will be unpacked and converted to pressure or depth data. However,
    the transducers will need to be calibrated at each use.
    '''

    def __init__(self, com_port, baud_rate, id):
        '''
        Initialize serial connection with a Pressure Transducer. Since multiple
        transducers may exist on the system, provide an ID for each transducer.

        Parameters:
            com_port: There serial communication port used to get data from the
                        pressure transducer.
            baud_rate: The baud rate to communicate with the transducers.
            id: An integer ID for the given transducer. By default this is 1, but
                if you are using multiple transducers, give each a unique id.
        Returns:
            N/A
        '''
        self.com_port = com_port
        self.transducer_serial = serial.Serial(com_port, baud_rate)
        self.id = id

        #initially set the pressure and depth_error to zero, this should be reset
        #by the calibration function
        self.pressure_error = 0
        self.depth_error = 0

        #TODO: Figure out these values!
        #scaling factor to convert raw data to pressure data
        self.pressure_scaling = 1

        #scaling factor to convert raw data to depth data
        self.depth_scaling = 1
    def get_pressure(self):
        '''
        Return the pressure in measurement of PSI.

        Parameters:
            N/A
        Returns:
            pressure_data: The pressure data measured in PSI
            None: If data cannot be retrieved, return None
        '''
        raw_pressure_data = self._unpack()

        #convert raw_pressure_data to pressure in PSI
        pressure_data = (raw_pressure_data * self.pressure_scaling) - self.pressure_error
        return pressure_data

    def get_depth(self):
        '''
        Return the depth of the AUV in feet.

        Parameters:
            N/A
        Returns:
            depth_data: The depth data measured in feet
            None: If the data cannot be retrieved, return None
        '''
        raw_pressure_data = self._unpack()
        depth_data = (raw_pressure_data * self.depth_scaling) - self.depth_error
        return depth_data

    def calibrate(self):
        pass

    def _unpack(self):
        '''
        Retrieve a single data packet from the transducer and unpack it into
        numberical form.

        Parameters:
            N/A
        Returns:
            raw_pressure_data: The raw pressure data received in the data packet.
            None: If an error occurs and/or no pressure data was received.
        '''
        try:
            if self.transducer_serial > 0:
                raw_pressure_data = int(self.transducer_serial.readline())
                return raw_pressure_data
        except RuntimeError:
            print("Couldn't receive any data from Pressure Transducer", self.id,
                    "on serial port", self.com_port)
            return None

class Pressure_Depth_Transducers(sensorHubBase):
    '''
    Receive Pressure and Depth data from each pressure transducer. Filter the data
    and fuse each sensors data for a less noisey reading using a Kalman Filter.
    '''
    def __init__(self, com_ports):
        '''
        Initialize communication with each pressure transducer. And set up MechOS
        node to communicate data over the MechOS network.

        Parameters:
            com_ports: A list of com ports that the pressure transducers are
                        connected to.

        Returns:
            N/A
        '''
        super(Pressure_Depth_Transducers, self).__init__()

        self.type = "PRESSURE_TRANSDUCERS"

        #ovveride the parent publisher attribute
        self.sensorHub_transducers = mechos.Node("SENSORHUB_PRESSURE_TRANSDUCERS")
        self.publisher = self.sensorHub_transducers.create_publisher("TRANS_DATA")

        self.pressure_transducers = []
        for index, com_port in enumerate(com_ports):
            #create set the com port and baud rate for each transducer
            self.pressure_transduders.append(Pressure_Tranducer(com_port,
                                                    baud_rate=115200, id=index))
    def receive_sensor_data(self):
        '''
        Receive the pressure and depth data from the pressure transducers. Fuse
        the data using a Kalman filter to get the best reading

        Parameters:
            N/A

        Returns:
            [pressure, depth]: List of the pressure and depth data if the data
                                is received properly
            False: If the data is not received properly.
        '''
        pressures = []
        depths = []

        for transducer in self.pressure_transducers:
            pressures.append(transducer.get_pressure())
            depths.append(transducer.get_depth())

        #Perfrom kalman filtering to obtain the most probable pressure and depth

        #TODO: KALMAN FILTER
        return [pressure, depth]

    def run(self):
        '''
        Continually get pressure and depth data from the pressure transducers and
        publish it to the MechOS network over the topic "TRANS_DATA"

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while(1):
            self.data = self.receive_sensor_data()

            if(self.data is not False):
                self.publish_data()

            time.sleep(0.25)
