from sensorHub import SensorHubBase
import serial

class DVL(SensorHubBase):

    def __init__(self):
        super(DVL, self).__init__()
        #Change type to match protobuf
        self.type = "DVL_DATA"
        self.serialObject = serial.Serial("/dev/ttyUSB5", 115200)

        #Taken from robosub-2018
        self.alertList = []
        self.getList = []
        self.ahrs = 0
        self.distanceToFloor = 0
        self.velocitiesXYZ = [0, 0, 0]  # Velocities for the DVL's coordinate system
        self.velTimesXYZ = [0, 0, 0]  # Time estimate for the velocities
        self.positionA = [0, 0, 0]  # North, East, Down


    def receiveData(self):
        return self.unpack()


    '''
    Taken From robosub-2018
    :Author Jared Guerrero
    '''
#TODO FIGURE OUT WHAT DATA WE NEED TO BE SENT. PROTOS STATE (up, x, y, err)
    def unpack(self):
        try:
            if self.serialObject.inWaiting() != 0:
                SYNC = hex(ord(self.serialObject.read()))
                if SYNC == "0xa5":
                    header = ord(self.serialObject.read())  # Use ord when dealing with 1 byte
                    ID = ord(self.serialObject.read())  # How many bytes in ensemble
                    family = ord(self.serialObject.read())  # How many bytes in ensemble
                    dataSize = self.serialObject.read(2)  # Specify number of bytes if greater than 1
                    dataChecksum = self.serialObject.read(2)  # How many bytes in ensemble
                    headerChecksum = self.serialObject.read(2)  # How many bytes in ensemble
                    if hex(ID) == "0x1b":  # If this is a Bottom Tracking Message
                        version = ord(self.serialObject.read())
                        offsetOfData = ord(self.serialObject.read())
                        serialNumber = self.serialObject.read(4)
                        year = ord(self.serialObject.read())
                        month = ord(self.serialObject.read())
                        day = ord(self.serialObject.read())
                        hour = ord(self.serialObject.read())
                        minute = ord(self.serialObject.read())
                        seconds = ord(self.serialObject.read())
                        microSec = self.serialObject.read(2)
                        numberOfBeams = self.serialObject.read(2)
                        error = self.serialObject.read(4)
                        status = self.serialObject.read(4)
                        soundSpeed = self.serialObject.read(4)
                        temperature = self.serialObject.read(4)
                        pressure = self.serialObject.read(4)
                        velBeam0 = self.serialObject.read(4)
                        velBeam1 = self.serialObject.read(4)
                        velBeam2 = self.serialObject.read(4)
                        velBeam3 = self.serialObject.read(4)
                        disBeam0 = self.serialObject.read(4)
                        disBeam0 = struct.unpack('<f', disBeam0)
                        disBeam1 = self.serialObject.read(4)
                        disBeam1 = struct.unpack('<f', disBeam1)
                        disBeam2 = self.serialObject.read(4)
                        disBeam2 = struct.unpack('<f', disBeam2)
                        disBeam3 = self.serialObject.read(4)
                        disBeam3 = struct.unpack('<f', disBeam3)
                        self.distanceToFloor = ((disBeam0[0]) + (disBeam1[0]) + (disBeam2[0]) + (disBeam3[0])) / 4
                        fomBeam0 = self.serialObject.read(4)
                        fomBeam1 = self.serialObject.read(4)
                        fomBeam2 = self.serialObject.read(4)
                        fomBeam3 = self.serialObject.read(4)
                        dt1Beam0 = self.serialObject.read(4)
                        dt1Beam1 = self.serialObject.read(4)
                        dt1Beam2 = self.serialObject.read(4)
                        dt1Beam3 = self.serialObject.read(4)
                        dt2Beam0 = self.serialObject.read(4)
                        dt2Beam1 = self.serialObject.read(4)
                        dt2Beam2 = self.serialObject.read(4)
                        dt2Beam3 = self.serialObject.read(4)
                        timeVelEstBeam0 = self.serialObject.read(4)
                        timeVelEstBeam1 = self.serialObject.read(4)
                        timeVelEstBeam2 = self.serialObject.read(4)
                        timeVelEstBeam3 = self.serialObject.read(4)
                        velX = self.serialObject.read(4)
                        velX = struct.unpack('<f', velX)
                        self.velocitiesXYZ[0] = velX[0]
                        velY = self.serialObject.read(4)
                        velY = struct.unpack('<f', velY)
                        self.velocitiesXYZ[1] = velY[0]
                        velZ1 = self.serialObject.read(4)
                        velZ1 = struct.unpack('<f', velZ1)
                        self.velocitiesXYZ[2] = velZ1[0]
                        velZ2 = self.serialObject.read(4)
                        fomX = self.serialObject.read(4)
                        fomY = self.serialObject.read(4)
                        fomZ1 = self.serialObject.read(4)
                        fomZ2 = self.serialObject.read(4)
                        dt1X = self.serialObject.read(4)
                        dt1Y = self.serialObject.read(4)
                        dt1Z1 = self.serialObject.read(4)
                        dt1Z2 = self.serialObject.read(4)
                        dt2X = self.serialObject.read(4)
                        dt2Y = self.serialObject.read(4)
                        dt2Z1 = self.serialObject.read(4)
                        dt2Z2 = self.serialObject.read(4)
                        timeVelEstX = self.serialObject.read(4)
                        timeVelEstX = struct.unpack('<f', timeVelEstX)  #
                        self.velTimesXYZ[0] = timeVelEstX[0]
                        timeVelEstY = self.serialObject.read(4)
                        timeVelEstY = struct.unpack('<f', timeVelEstY)
                        self.velTimesXYZ[1] = timeVelEstY[0]
                        timeVelEstZ1 = self.serialObject.read(4)
                        timeVelEstZ1 = struct.unpack('<f', timeVelEstZ1)
                        self.velTimesXYZ[2] = timeVelEstZ1[0]
                        timeVelEstZ2 = self.serialObject.read(4)

                    return [self.velocitiesXYZ, self.velTimesXYZ]

                else:
                    self.serialObject.flushInput()

        except Exception as msg:
            print("Can't receive data from DVL: {}".format(msg))

if __name__ == "__main__":
    dvl = DVL()
    dvl.run()
