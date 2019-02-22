
import sys
import os
#\/\/CHECK LOCATION OF FILE!!!\/\/#
PROTO_PATH = os.path.join("..", "..", "Proto") #<---- may need to change
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

#from sensorHub import SensorHubBase
from MechOS import mechos
import Mechatronics_pb2
from PyQt5 import QtCore, QtGui
#form remoteControl import Calibration, Regular

class RemoteControl() :
    
    def __init__(self) :
        '''
        
        
        Parameters:
            N/A
        Returns:
            N/A
        '''         
        
        
        #change data type
        #self.type = "Remote"
        
        #set up coms port?
        #self.remote_coms_port = com_port #<<--passed argument
        
        #Define a mechOS node and subscriber
        self.sensorData = mechos.Node("Data_Node")
        self.sensorData.create_subscriber("Remote Control", self.unpack)
        #self.sensorData.create_subscriber("AHRS_DATA", self.updateAHRSData)
        #self.sensorData.create_subscriber("DVL_DATA", self.updateDVLData)
        #self.publisher = self.sensorData.create_publisher("Pick a name, a meaningful name...")
    
    def updateAHRSData(self, ahrs_data) :
        #Probably won't use
        ahrs_data_proto = Mechatronics_pb2.Mechatronics()
        ahrs_data_proto.ParseFromString(ahrs_data)
        ahrsDataList = [ahrs_data_proto.ahrs.yaw, ahrs_data_proto.ahrs.pitch, ahrs_data_proto.ahrs.roll]
    
    def updateDVLData(self, dvl_data) :
        #Probably won't use
        dvl_data_proto = Mechatronics_pb2.Mechatronics()
        dvl_data_proto.ParseFromString(dvl_data)
        dvlDataList = [dvl_data_proto.dvl.up, dvl_data_proto.dvl.x, dvl_data_proto.dvl.y, dvl_data_proto.dvl.err]
        
    def receive_sensor_data(self) :
        '''
        
        
        Parameters:
            N/A
        Returns:
            N/A
        '''        
        pass
    
    def unpack(self, sensor_data) :
        sensor_data_proto = Mechatronics_pb2.Mechatronics()
        sensor_data_proto.parseFromString(sensor_data)
        
        #ahrs unpack
        ahrsData = [sensor_data_proto.ahrs.yaw, 
                    sensor_data_proto.ahrs.pitch, 
                    sensor_data_proto.ahrs.roll]
        #dvl unpack
        dvlData = [sensor_data_proto.dvl.up, 
                   sensor_data_proto.dvl.x, 
                   sensor_data_proto.dvl.y, 
                   sensor_data_proto.dvl.err]
        
        #hydrophone unpack
        hydroData = [sensor_data_proto.hydros.first,
                     sensor_data_proto.hydros.second]
        
        #leakDetect unpack
        leakData = [sensor_data_proto.leakDetect.isLeaking]
        '''
        #pmud unpack
        pmudData = [sensor_data_proto.pmud.voltage,
                    sensor_data_proto.pmud.current,
                    sensor_data_proto.pmud.isSafe,
                    sensor_data_proto.pmud.kill]
        '''
        #TODO: pneumatics
        #pneumatical brahhh
        
        #thruster unpack
        thrusterData = [sensor_data_proto.thruster.thruster_1,
                        sensor_data_proto.thruster.thruster_2,
                        sensor_data_proto.thruster.thruster_3,
                        sensor_data_proto.thruster.thruster_4,
                        sensor_data_proto.thruster.thruster_5,
                        sensor_data_proto.thruster.thruster_6,
                        sensor_data_proto.thruster.thruster_7,
                        sensor_data_proto.thruster.thruster_8]
        
        #
        
    
    def run(self) :
        '''
        
        
        Parameters:
            N/A
        Returns:
           N/A
        '''
        while True :
            
            '''TODO
            if True :
                calibration = Calibration()
            else :
                regular = Regular()
            '''
            pass

if __name__ == "__main__" :
    remote = RemoteControl()
    remote.run()