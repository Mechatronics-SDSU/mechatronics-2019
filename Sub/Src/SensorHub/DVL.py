'''
    Adapted from the origional dvl.py by Jared Guerrero, and in Accordance with Mechatronics Etiquite and
    the Creative Commons Licence LLC.

    Current Maintainers: Christian Gould, David Walker-Howell
    Email: Christian.d.gould@gmail.com, piercedhowell@gmail.com
    Last Modified: 06/22/2019
'''
import sys
import os

import serial
import time
import struct
import numpy as np
import threading

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from MechOS import mechos

class DVL_DATA_DRIVER:
    '''
    Communicate with the Norteck DVL module and retieve the velocities of the of the
    AUV. These velocities can be used to determine the position of the AUV via
    integration.
    '''
    def __init__(self, com_port):
        '''
        Initialize communication with the Norteck DVL.
        Parameters:
            com_port: The serial communication port communicating with the DVL.
        Returns:
            N/A
        '''
        self.dvl_serial = serial.Serial(com_port, 115200, timeout=1)

        #Dvl data is where the velocities and time velocities estimations are
        #stored
        self.dvl_data = [0, 0, 0, 0, 0, 0]



    def _unpack(self):
        '''
        The DVL has been setup to be cyclic, wherupon the Headerbye 'sync' is used to determine where the string restarts

        Parameters:

            variable is set true. If false, the velocities will be in meters per second.

        Returns:
            [vel_x, vel_y, vel_z, time_vel_est_x, time_vel_est_y, time_vel_est_z]: This function
            returns the x, y, z velocities and the estimated times that these velocities were maintained.
            The combination of these values can be used to help determine the position of the AUV. Note,
            if DVL data is not able to be obtained, None will be returned.

        #important Variable Descriptions#
        -----------
        SYNC -- Determines the sync byte to determine the system
        ID -- Determines the type of Data that will be Sent as a stream: Note that this is changeable

        NOTE: The Velocity will be returned from the DVL in m/s
        We Make a conversion to ft/s

        SEE: DVL integrators Guide from NORTEC There is one Freely avaliable online, (it's on a git)

        The Velocities must be unpacked from a set of four bytes, as it is packed in a C struct
        NOTE: the C struct module 'struct' in python will unwrap these bytes into a tuple
        Be sure to index this to get the data inside the touple to be consistent with Protobuf binaries
        '''
        
        try:
            prev_time = time.time()
            if self.dvl_serial.in_waiting:
                SYNC = hex(ord(self.dvl_serial.read()))
                #print SYNC
                if SYNC == "0xa5":

                    header = ord(self.dvl_serial.read())  # Use ord when dealing with 1 byte
                    ID = ord(self.dvl_serial.read())  # How many bytes in ensemble
                    family = ord(self.dvl_serial.read())  # How many bytes in ensemble
                    dataSize = self.dvl_serial.read(2)  # Specify number of bytes if greater than 1
                    dataChecksum = self.dvl_serial.read(2)  # How many bytes in ensemble
                    headerChecksum = self.dvl_serial.read(2)  # How many bytes in ensemble
                    if hex(ID) == "0x1b":  # If this is a Bottom Tracking Message
                        """
                        version = ord(self.dvl_serial.read())
                        offset_of_Data = ord(self.dvl_serial.read())
                        serial_number = self.dvl_serial.read(4)
                        year = ord(self.dvl_serial.read())
                        month = ord(self.dvl_serial.read())
                        day = ord(self.dvl_serial.read())
                        hour = ord(self.dvl_serial.read())
                        minute = ord(self.dvl_serial.read())
                        seconds = ord(self.dvl_serial.read())
                        microsec = self.dvl_serial.read(2)
                        number_of_beams = self.dvl_serial.read(2)
                        error = self.dvl_serial.read(4)
                        status = self.dvl_serial.read(4)
                        sound_speed = self.dvl_serial.read(4)
                        temperature = self.dvl_serial.read(4)
                        pressure = self.dvl_serial.read(4)
                        vel_beam_0 = self.dvl_serial.read(4)
                        vel_beam_1 = self.dvl_serial.read(4)
                        vel_beam_2 = self.dvl_serial.read(4)
                        vel_beam_3 = self.dvl_serial.read(4)
                        dis_beam_0 = self.dvl_serial.read(4)
                        dis_beam_0 = struct.unpack('<f', dis_beam_0)
                        dis_beam_1 = self.dvl_serial.read(4)
                        dis_beam_1 = struct.unpack('<f', dis_beam_1)
                        dis_beam_2 = self.dvl_serial.read(4)
                        dis_beam_2 = struct.unpack('<f', dis_beam_2)
                        dis_beam_3 = self.dvl_serial.read(4)
                        dis_beam_3 = struct.unpack('<f', dis_beam_3)
                        #self.distanceToFloor = ((dis_beam_0[0]) + (dis_beam_1[0]) + (dis_beam_2[0]) + (dis_beam_3[0])) / 4
                        fombeam_0 = self.dvl_serial.read(4)
                        fombeam_1 = self.dvl_serial.read(4)
                        fombeam_2 = self.dvl_serial.read(4)
                        fombeam_3 = self.dvl_serial.read(4)
                        dt1beam_0 = self.dvl_serial.read(4)
                        dt1beam_1 = self.dvl_serial.read(4)
                        dt1beam_2 = self.dvl_serial.read(4)
                        dt1beam_3 = self.dvl_serial.read(4)
                        dt2beam_0 = self.dvl_serial.read(4)
                        dt2beam_1 = self.dvl_serial.read(4)
                        dt2beam_2 = self.dvl_serial.read(4)
                        dt2beam_3 = self.dvl_serial.read(4)
                        time_vel_est_beam_0 = self.dvl_serial.read(4)
                        time_vel_est_beam_1 = self.dvl_serial.read(4)
                        time_vel_est_beam_2 = self.dvl_serial.read(4)
                        time_vel_est_beam_3 = self.dvl_serial.read(4)
                        """
                        self.dvl_serial.read(112)
                        vel_y = self.dvl_serial.read(4)
                        vel_y = struct.unpack('<f', vel_y)
                        self.dvl_data[1] = vel_y[0]
                        vel_x = self.dvl_serial.read(4)
                        vel_x = struct.unpack('<f', vel_x)
                        self.dvl_data[0] = vel_x[0]
                        vel_z1 = self.dvl_serial.read(4)
                        vel_z1 = struct.unpack('<f', vel_z1)
                        self.dvl_data[2] = vel_z1[0]
                        """
                        velZ2 = self.dvl_serial.read(4)
                        fomX = self.dvl_serial.read(4)
                        fomY = self.dvl_serial.read(4)
                        fomZ1 = self.dvl_serial.read(4)
                        fomZ2 = self.dvl_serial.read(4)
                        dt1X = self.dvl_serial.read(4)
                        dt1Y = self.dvl_serial.read(4)
                        dt1Z1 = self.dvl_serial.read(4)
                        dt1Z2 = self.dvl_serial.read(4)
                        dt2X = self.dvl_serial.read(4)
                        dt2Y = self.dvl_serial.read(4)
                        dt2Z1 = self.dvl_serial.read(4)
                        dt2Z2 = self.dvl_serial.read(4)
                        time_vel_est_y = self.dvl_serial.read(4)
                        time_vel_est_y = struct.unpack('<f', time_vel_est_y)  #
                        self.dvl_data[4] = time_vel_est_y[0]
                        time_vel_est_x = self.dvl_serial.read(4)
                        time_vel_est_x = struct.unpack('<f', time_vel_est_x)
                        self.dvl_data[3] = time_vel_est_x[0]
                        time_vel_est_z1 = self.dvl_serial.read(4)
                        time_vel_est_z1 = struct.unpack('<f', time_vel_est_z1)
                        self.dvl_data[5] = time_vel_est_z1[0]
                        time_vel_est_z2 = self.dvl_serial.read(4)
                        #ensemble = self.getDistanceTraveled()
                        """
                        self.dvl_serial.read(68)
                        return self.dvl_data
                    else:
                        self.dvl_serial.reset_input_buffer()
                else:
                   # self.dvl_serial.flushInput()
                   self.dvl_serial.reset_input_buffer()

        except Exception as e:
            print("[ERROR]: DVL.py --> Error attemping to receive DVL data via serial com. Error: ", e)

class DVL_THREAD(threading.Thread):
    '''
    Primary thread to communicate with the DVL and retrieve its data.
    '''

    def __init__(self,com_port):
        '''
        Initialize the thread to communicate with the DVL. Establish serial communication
        with the dvl and initialize the queue for data.

        Parameters:
            com_port: The serial communication port connect to the dvl.
        Returns:
            N/A
        '''
        super(DVL_THREAD, self).__init__()

        self.daemon = True

        #COMMUNICATON: SERIAL PORT
        self.DVL_PORT = com_port

        #DVL: OBJECT
        self.norteck_dvl = DVL_DATA_DRIVER(com_port)

        #MECHOS:NETWORK HOSTS

        #THREAD PARAMS
        self.threading_lock = threading.Lock()

        #The dvl data queue is where new dvl data is pushed onto. When this data
        #is retrieved for navigation, it should be popped of. This queue should be
        #used in the LIFO order.
        self.dvl_data_queue = []


    def run(self):
        '''
        Continually Request data from the Norteck DVL and add it to the dvl data
        queue if it is available.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while(True):

            try:
                #Attempt to retrieve dvl data.
                dvl_data_packet = self.norteck_dvl._unpack()
                #NOTE: Possibly need to add more error checking
                
                if((dvl_data_packet != None) and (dvl_data_packet != [0])):
                    self.dvl_data_queue.append(dvl_data_packet)
                    

            except Exception as e:
                print("[ERROR]: Could not properly recieve DVL data. Error:", e)

            #Give time for thread loop. Helps save power consumption.
            time.sleep(0.001)
if __name__== '__main__':
    DVL = DVL_THREAD('/dev/ttyUSB1')
    DVL.run()
