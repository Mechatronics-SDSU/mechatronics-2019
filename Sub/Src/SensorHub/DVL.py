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
        self.curr_time = np.array([0, 0, 0], dtype=float)
        self.prev_vel = np.array([0,0,0], dtype=float)
        self.displacement = np.array([0,0,0], dtype=float)

        #ADDED AS TEST
        self.velocitiesXYZ = [0, 0, 0]  # Velocities for the DVL's coordinate system
        self.velTimesXYZ = [0, 0, 0]  # Time estimate for the velocities

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


        SYNC_flag = False
        velZ = [0]
        velX = [0]
        velY = [0]
        timeVelEstZ = 0
        timeVelEstX = 0
        timeVelEstY = 0
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

                    #Get velocities in x,y, and z directions
                    velX = self.DVLCom.read(4)
                    velX = struct.unpack('<f', velX)
                    velY = self.DVLCom.read(4)
                    velY = struct.unpack('<f', velY)
                    velZ = self.DVLCom.read(4)
                    velZ = struct.unpack('<f', velZ)

                    self.DVLCom.read(48) #Read extra unwanted data

                    #Read the time duration estimation values of the velocities.
                    timeVelEstX = self.DVLCom.read(4)
                    timeVelEstX = struct.unpack('<f', timeVelEstX)[0]
                    timeVelEstY = self.DVLCom.read(4)
                    timeVelEstY = struct.unpack('<f', timeVelEstY)[0]
                    timeVelEstZ = self.DVLCom.read(4)
                    timeVelEstZ = struct.unpack('<f', timeVelEstZ)[0]

                self.DVLCom.flush()
        #TODO: Clean this code up!
        # conversion to ft/s
        if inFeet==True:
            velocities = np.array([velZ[0], velX[0], velY[0]]) * 3.28084
            vel_times = np.array([timeVelEstZ, timeVelEstX, timeVelEstY])
            return(np.concatenate((velocities, vel_times), axis=None))
        # normal return as m/s
        return (np.array([velZ[0], velX[0], velY[0]]), np.array([timeVelEstZ, timeVelEstX, timeVelEstY]))
        '''
        try:
            if self.DVLCom.inWaiting() != 0:
                SYNC = hex(ord(self.DVLCom.read()))
                #print SYNC
                if SYNC == "0xa5":

                    header = ord(self.DVLCom.read())  # Use ord when dealing with 1 byte
                    ID = ord(self.DVLCom.read())  # How many bytes in ensemble
                    family = ord(self.DVLCom.read())  # How many bytes in ensemble
                    dataSize = self.DVLCom.read(2)  # Specify number of bytes if greater than 1
                    dataChecksum = self.DVLCom.read(2)  # How many bytes in ensemble
                    headerChecksum = self.DVLCom.read(2)  # How many bytes in ensemble
                    if hex(ID) == "0x1b":  # If this is a Bottom Tracking Message
                        version = ord(self.DVLCom.read())
                        offsetOfData = ord(self.DVLCom.read())
                        serialNumber = self.DVLCom.read(4)
                        year = ord(self.DVLCom.read())
                        month = ord(self.DVLCom.read())
                        day = ord(self.DVLCom.read())
                        hour = ord(self.DVLCom.read())
                        minute = ord(self.DVLCom.read())
                        seconds = ord(self.DVLCom.read())
                        microSec = self.DVLCom.read(2)
                        numberOfBeams = self.DVLCom.read(2)
                        error = self.DVLCom.read(4)
                        status = self.DVLCom.read(4)
                        soundSpeed = self.DVLCom.read(4)
                        temperature = self.DVLCom.read(4)
                        pressure = self.DVLCom.read(4)
                        velBeam0 = self.DVLCom.read(4)
                        velBeam1 = self.DVLCom.read(4)
                        velBeam2 = self.DVLCom.read(4)
                        velBeam3 = self.DVLCom.read(4)
                        disBeam0 = self.DVLCom.read(4)
                        disBeam0 = struct.unpack('<f', disBeam0)
                        disBeam1 = self.DVLCom.read(4)
                        disBeam1 = struct.unpack('<f', disBeam1)
                        disBeam2 = self.DVLCom.read(4)
                        disBeam2 = struct.unpack('<f', disBeam2)
                        disBeam3 = self.DVLCom.read(4)
                        disBeam3 = struct.unpack('<f', disBeam3)
                        self.distanceToFloor = ((disBeam0[0]) + (disBeam1[0]) + (disBeam2[0]) + (disBeam3[0])) / 4
                        fomBeam0 = self.DVLCom.read(4)
                        fomBeam1 = self.DVLCom.read(4)
                        fomBeam2 = self.DVLCom.read(4)
                        fomBeam3 = self.DVLCom.read(4)
                        dt1Beam0 = self.DVLCom.read(4)
                        dt1Beam1 = self.DVLCom.read(4)
                        dt1Beam2 = self.DVLCom.read(4)
                        dt1Beam3 = self.DVLCom.read(4)
                        dt2Beam0 = self.DVLCom.read(4)
                        dt2Beam1 = self.DVLCom.read(4)
                        dt2Beam2 = self.DVLCom.read(4)
                        dt2Beam3 = self.DVLCom.read(4)
                        timeVelEstBeam0 = self.DVLCom.read(4)
                        timeVelEstBeam1 = self.DVLCom.read(4)
                        timeVelEstBeam2 = self.DVLCom.read(4)
                        timeVelEstBeam3 = self.DVLCom.read(4)
                        velX = self.DVLCom.read(4)
                        velX = struct.unpack('<f', velX)
                        self.velocitiesXYZ[0] = velX[0]
                        velY = self.DVLCom.read(4)
                        velY = struct.unpack('<f', velY)
                        self.velocitiesXYZ[1] = velY[0]
                        velZ1 = self.DVLCom.read(4)
                        velZ1 = struct.unpack('<f', velZ1)
                        self.velocitiesXYZ[2] = velZ1[0]
                        velZ2 = self.DVLCom.read(4)
                        fomX = self.DVLCom.read(4)
                        fomY = self.DVLCom.read(4)
                        fomZ1 = self.DVLCom.read(4)
                        fomZ2 = self.DVLCom.read(4)
                        dt1X = self.DVLCom.read(4)
                        dt1Y = self.DVLCom.read(4)
                        dt1Z1 = self.DVLCom.read(4)
                        dt1Z2 = self.DVLCom.read(4)
                        dt2X = self.DVLCom.read(4)
                        dt2Y = self.DVLCom.read(4)
                        dt2Z1 = self.DVLCom.read(4)
                        dt2Z2 = self.DVLCom.read(4)
                        timeVelEstX = self.DVLCom.read(4)
                        timeVelEstX = struct.unpack('<f', timeVelEstX)  #
                        self.velTimesXYZ[0] = timeVelEstX[0]
                        timeVelEstY = self.DVLCom.read(4)
                        timeVelEstY = struct.unpack('<f', timeVelEstY)
                        self.velTimesXYZ[1] = timeVelEstY[0]
                        timeVelEstZ1 = self.DVLCom.read(4)
                        timeVelEstZ1 = struct.unpack('<f', timeVelEstZ1)
                        self.velTimesXYZ[2] = timeVelEstZ1[0]
                        timeVelEstZ2 = self.DVLCom.read(4)
                        #ensemble = self.getDistanceTraveled()

                    return [self.velocitiesXYZ, self.velTimesXYZ]

                else:
                    self.DVLCom.flushInput()

        except Exception as msg:
            print("Can't receive data from DVL:", msg)

    #DEPRECATE THIS FUNCTION. Position calcs moved to sensor_driver.py
    """
    def __get_displacement(self):
        '''
            This function calculates the displacement of the sub in the X Y Z
            directions (since the ). This function will also return the velocities in each direction
            since the velocities are needed to calculate the displacement.

            RETURNS: A numpy array of [velZ, velX, velY, dispZ, dispX, dispY]
        '''
        self.prev_vel = self.curr_vel
        self.curr_vel, self.curr_time = self.__get_velocity()

        #initial CALCULATION: Trapezoid Rule
        self.displacement += (.125)*(self.curr_vel + self.prev_vel)/2

        return np.concatenate((self.curr_vel, self.displacement), axis=None)
    """
    def get_PACKET(self):
        return self.__get_velocity()

class DVL_THREAD(threading.Thread):
    '''

    Communicate with the Nortek DVL

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

            try:

                if(self.reset_integration_flag):

                    self.Norteck_DVL.reset_integration()
                    self.reset_integration_flag = False #Reset the flag
                #with threading.Lock():
                dvl_data_packet = self.Norteck_DVL.get_PACKET()

                if((dvl_data_packet != None) and (dvl_data_packet != [0])):

                    if(((dvl_data_packet[0])[0] < -32) or (dvl_data_packet[0])[1] < -32):
                        print("[WARNING]: DVL velocity less than minimum of -32")
                        continue
                    self.PACKET = dvl_data_packet

            except Exception as e:
                print("[ERROR]: Could not properly recieve DVL data. Error:", e)

            #time.sleep(0.4)

if __name__== '__main__':
    DVL = DVL_THREAD('/dev/ttyUSB1')
    DVL.run()
