'''
    Adapted from the origional dvl.py by Jared Guerrero, and in Accordance with Mechatronics Etiquite and
    the Creative Commons Licence LLC.

    Current Maintainers: Christian Gould, David Walker-Howell
    Email: Christian.d.gould@gmail.com
    Last Modified 1/29/2019
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
    def __init__(self, comport):
        self.DVLCom = serial.Serial(comport, 115200, timeout=1)

        #Velocity Sync
        self.curr_vel = np.array([0,0,0], dtype=float)
        self.prev_vel = np.array([0,0,0], dtype=float)
        self.displacement = np.array([0,0,0], dtype=float)

    def reset_integration(self):
        '''
        Set the current displacement to zero.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        for i in range(3):
            self.displacement[i] = 0.0

    def __get_velocity(self, inFeet=True):
        '''
        The DVL has been setup to be cyclic, wherupon the Headerbye 'sync' is used to determine where the string restarts

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
        SYNC_flag = False
        velZ = [0]
        velX = [0]
        velY = [0]
        while(not SYNC_flag):
        #if(self.DVLCom.inWaiting() > 154):
            SYNC = hex(ord(self.DVLCom.read()))
            if(SYNC == "0xa5"):
                SYNC_flag = True
                header = ord(self.DVLCom.read())
                ID     = ord(self.DVLCom.read())
                family = ord(self.DVLCom.read())
                dataSize = self.DVLCom.read(2)
                dataChecksum = self.DVLCom.read(2)
                headerChecksum = self.DVLCom.read(2)

                if(hex(ID) == "0x1b"):
                    self.DVLCom.read(16)
                    error = self.DVLCom.read(4)
                    error = struct.unpack('<f', error)

                    self.DVLCom.read(112)

                    velX = self.DVLCom.read(4)
                    velX = struct.unpack('<f', velX)
                    velY = self.DVLCom.read(4)
                    velY = struct.unpack('<f', velY)
                    velZ = self.DVLCom.read(4)
                    velZ = struct.unpack('<f', velZ)

                self.DVLCom.flush()

        # conversion to ft/s
        if inFeet==True:
            return np.array([velZ[0], velX[0], velY[0]]) * 3.28084

        # normal return as m/s
        return np.array([velZ[0], velX[0], velY[0]])

    def __get_displacement(self):
        '''
            This function calculates the displacement of the sub in the X Y Z
            directions. This function will also return the velocities in each direction
            since the velocities are needed to calculate the displacement.

            RETURNS: A numpy array of [velZ, velX, velY, dispZ, dispX, dispY]
        '''
        self.prev_vel = self.curr_vel
        self.curr_vel = self.__get_velocity()

        #initial CALCULATION: Trapezoid Rule
        self.displacement += (.125)*(self.curr_vel + self.prev_vel)/2

        '''
        The concept, is that we take the average of the two points, and multiply them by
        their rate of change


        (b - a)* (f(a) + f(b))/2

        --(b - a) = 8hz or .125s(p)

        '''

        #TODO
        #Continuous CALCULATION Simpsons Rule
        '''

        To make the most of our calculations, we will utilize simpsons rule
        Following our use of Trapezoid Rule,

        '''

        return np.concatenate((self.curr_vel, self.displacement), axis=None)

    def get_PACKET(self):
        return self.__get_displacement()

class DVL_THREAD(threading.Thread):
    '''

    Communicate with the Nortek DVL

    ...

    RETURN: nothing

    PARAMETERS: NONE

    '''

    def __init__(self,comport):
        super(DVL_THREAD, self).__init__()

        self.daemon = True

        #COMMUNICATON: SERIAL PORT
        self.DVL_PORT = comport

        #DVL: OBJECT
        self.Norteck_DVL = DVL_DATA_DRIVER(comport)

        #MECHOS:NETWORK HOSTS

        #THREAD PARAMS
        self.threading_lock = threading.Lock()


        #PACKET: VELOCITY(XYZ), DISPLACEMENT(XYZ)
        self.PACKET = np.array([0,0,0,0,0,0])

        #Set this flag to zero out the integration
        self.reset_integration_flag = True


    def run(self):
        '''
        Request data from the Norteck DVL and publish it to the Network
        '''
        while(True):

            if(self.reset_integration_flag):
                
                self.Norteck_DVL.reset_integration()
                self.reset_integration_flag = False #Reset the flag
            #with threading.Lock():
            self.PACKET = self.Norteck_DVL.get_PACKET()
            #print(self.PACKET) #uncomment to test

            time.sleep(0.4)

if __name__== '__main__':
    DVL = DVL_THREAD('/dev/ttyUSB1')
    DVL.run()
