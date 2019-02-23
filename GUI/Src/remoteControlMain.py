
import sys
import os
#\/\/CHECK LOCATION OF FILE!!!\/\/#
PROTO_PATH = os.path.join("Proto") #<---- may need to change
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

from MechOS import mechos
import Mechatronics_pb2
#from PyQt5 import QtCore, QtGui
#from remoteControl import Calibration, Regular

class RemoteControl() :
    
    def __init__(self) :
        '''
        
        
        Parameters:
            N/A
        Returns:
            N/A
        '''         
        #Define a mechOS node and subscriber
        self.sensorData = mechos.Node("Data_Node")
        self.sensorData.create_subscriber("Remote Control", self.unpack)
        #self.publisher = self.sensorData.create_publisher("Pick a name, a meaningful name...")
    
    def unpack(self, sensor_data) :
        '''
        unpack method for parsing the protobuff for all relevant data.
        
        Parameters:
            sensor_data passed by mechOS node in subscriber callback
        Returns:
            N/A
        '''         
        #get the big ol' protobuff and parse from string
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
        
        #pmud unpack
        pmudData = [sensor_data_proto.pmud.voltage,
                    sensor_data_proto.pmud.current,
                    sensor_data_proto.pmud.isSafe,
                    sensor_data_proto.pmud.kill]
        
        #pneumatical brahhh
        pneumaticData = [sensor_data_proto.pneumatics.thing]
        
        #thruster unpack
        thrusterData = [sensor_data_proto.thruster.thruster_1,
                        sensor_data_proto.thruster.thruster_2,
                        sensor_data_proto.thruster.thruster_3,
                        sensor_data_proto.thruster.thruster_4,
                        sensor_data_proto.thruster.thruster_5,
                        sensor_data_proto.thruster.thruster_6,
                        sensor_data_proto.thruster.thruster_7,
                        sensor_data_proto.thruster.thruster_8]
        
        #pid unpack
        pidData = [sensor_data_proto.pid.PID_channel,
                   sensor_data_proto.pid.k_p,
                   sensor_data_proto.pid.k_i,
                   sensor_data_proto.pid.k_d]
        
        #pid_error unpack
        pidErrorData = [sensor_data_proto.pid_error.roll_error,
                        sensor_data_proto.pid_error.pitch_error,
                        sensor_data_proto.pid_error.yaw_error,
                        sensor_data_proto.pid_error.x_error,
                        sensor_data_proto.pid_error.y_error,
                        sensor_data_proto.pid_error.z_error]
        
        #pressure transducer unpack
        pressureTransData = [sensor_data_proto.pressureTrans.depth] 
        
        #weapons unpack
        fireWeaponsData = [sensor_data_proto.guiComm.fireWeapons1,
                           sensor_data_proto.guiComm.fireWeapons2, 
                           sensor_data_proto.guiComm.fireWeapons3,
                           sensor_data_proto.guiComm.fireWeapons4,
                           sensor_data_proto.guiComm.fireWeapons5]
    
    
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