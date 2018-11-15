'''
:Author: Cole Brower <cole.brower@gmail.com>
:Date: Created on Oct 30, 2018
:Description: Helper class for packaging protocol buffers
'''

import sys
sys.path.append("../")

import Mechatronics_pb2

'''
This function takes in data in a buffer array and a type to then store in a protobuf

Throws:
    Exception if the data isn't formatted properly.
    Exception if the type does not exist.
'''
def packageProtobuf(protoType, data):
    proto = Mechatronics_pb2.Mechatronics()
    #TODO May have to cast data to the correct type
    if protoType == "AHRS_DATA":
        if len(data) != 3: # Length of AHRS Message TODO remove hardcoded values
            _raiseTypeException(protoType)
        proto.type       = Mechatronics_pb2.AHRS_DATA #TODO CHECK THIS
        proto.ahrs.yaw   = data[0]
        proto.ahrs.pitch = data[1]
        proto.ahrs.roll  = data[2]
    elif protoType == "DVL_DATA":
        if len(data) != 4:
            _raiseTypeException(protoType)
        proto.type    = Mechatronics_pb2.DVL_DATA
        proto.dvl.up  = data[0]
        proto.dvl.x   = data[1]
        proto.dvl.y   = data[2]
        proto.dvl.err = data[3]
    elif protoType == "hydrophones":
        if len(data) != 2:
            _raiseTypeException(protoType)
        proto.type          = Mechatronics_pb2.HYDROPHONES
        proto.hydros.first  = data[0]
        proto.hydros.second = data[1]
    elif protoType == "leakDetect":
        if len(data) != 1:
            _raiseTypeException(protoType)
        proto.type                 = Mechatronics_pb2.LEAK_DETECTION
        proto.leakDetect.isLeaking = data[0]
    elif protoType == "PMUD":
        if len(data) != 4:
            _raiseTypeException(protoType)
        proto.type         = Mechatronics_pb2.PMUD_DATA
        proto.pmud.voltage = data[0]
        proto.pmud.current = data[1]
        proto.pmud.isSafe  = data[2]
        proto.pmud.kill    = data[3]
    elif protoType == "pneumatics":
        if len(data) != 1:
            _raiseTypeException(protoType)
        proto.type = Mechatronics_pb2.PNEUMATICS
        for d in data[0]:
            proto.pneumatics.thing.append(d) #TODO Check syntax may be add
    elif protoType == "pressureTransducers":
        if len(data) != 1:
            _raiseTypeException(protoType)
        proto.type = Mechatronics_pb2.PRESSURE_TRANSDUCERS
        proto.pressureTrans.depth = data[0]
    else:
        raise Exception("Unknown protobuf type: {}".format(protoType))
    return proto

def _raiseTypeException(protoType):
    raise Exception("Invalid data format for type: {}".format(protoType))
