'''
:Author: Cole Brower <cole.brower@gmail.com>
:Date: Created on Oct 30, 2018
:Description: Helper class for packaging protocol buffers
'''

from os.path import dirname, realpath
import sys
sys.path.append(dirname(realpath(__file__)) + "/../")

import Mechatronics_pb2
import guiComm_pb2

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
        if len(data) != 3: # TODO Remove hard coded values
            _raiseTypeException(protoType)
        proto.type       = Mechatronics_pb2.AHRS_DATA
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
    elif protoType == "HYDROPHONES":
        if len(data) != 2:
            _raiseTypeException(protoType)
        proto.type          = Mechatronics_pb2.HYDROPHONES
        proto.hydros.first  = data[0]
        proto.hydros.second = data[1]
    elif protoType == "LEAK_DETECT":
        if len(data) != 1:
            _raiseTypeException(protoType)
        proto.type                 = Mechatronics_pb2.LEAK_DETECTION
        proto.leakDetect.isLeaking = data[0]
    elif protoType == "PMUD_DATA":
        if len(data) != 4:
            _raiseTypeException(protoType)
        proto.type         = Mechatronics_pb2.PMUD_DATA
        proto.pmud.voltage = data[0]
        proto.pmud.current = data[1]
        proto.pmud.isSafe  = data[2]
        proto.pmud.kill    = data[3]
    elif protoType == "PNEUMATICS":
        if len(data) != 1:
            _raiseTypeException(protoType)
        proto.type = Mechatronics_pb2.PNEUMATICS
        for d in data[0]:
            proto.pneumatics.thing.append(d) #TODO Check syntax may be add
    elif protoType == "PRESSURE_TRANSDUCERS":
        if len(data) != 1:
            _raiseTypeException(protoType)
        proto.type = Mechatronics_pb2.PRESSURE_TRANSDUCERS
        proto.pressureTrans.depth = data[0]
    elif protoType == "GUI_COMM":
        if data[0] == "START_DEBUG":
            proto.guiComm.type = guiComm_pb2.START_DEBUG
        elif data[0] == "START_AUTO":
            proto.guiComm.type = guiComm_pb2.START_AUTO
        elif data[0] == "STOP":
            proto.guiComm.type = guiComm_pb2.STOP
        elif data[0] == "RESET_MISSIONS":
            proto.guiComm.type = guiComm_pb2.RESET_MISSIONS
        elif data[0] == "MISSION_LIST":
            proto.guiComm.type = guiComm_pb2.MISSION_LIST
            proto.guiComm.jsonMissions = data[1]
        elif data[0] == "SKIP_MISSION":
            proto.guiComm.type = guiComm_pb2.SKIP_MISSION
        elif data[0] == "PREVIOUS_MISSION":
            proto.guiComm.type = guiComm_pb2.PREVIOUS_MISSION
        elif data[0] == "ABSOLUTE_TRANSLATE":
            proto.guiComm.type = guiComm_pb2.ABSOLUTE_TRANSLATE
            proto.guiComm.x = data[1]
            proto.guiComm.y = data[2]
            proto.guiComm.z = data[3]
        elif data[0] == "RELATIVE_TRANSLATE":
            proto.guiComm.type = guiComm_pb2.RELATIVE_TRANSLATE
            proto.guiComm.x = data[1]
            proto.guiComm.y = data[2]
            proto.guiComm.z = data[3]
        elif data[0] == "ROTATE":
            proto.guiComm.type = guiComm_pb2.ROTATE
            proto.guiComm.yaw = data[1]
            proto.guiComm.pitch = data[2]
            proto.guiComm.roll = data[3]
        elif data[0] == "ADD_MISSION":
            proto.guiComm.type = guiComm_pb2.ADD_MISSION
            proto.guiComm.jsonMissions = data[1]
        elif data[0] == "REMOVE_MISSION":
            proto.guiComm.type = guiComm_pb2.REMOVE_MISSION
            proto.guiComm.jsonMissions = data[1]
        elif data[0] == "START_MANUAL":
            proto.guiComm.type = guiComm_pb2.START_MANUAL
        elif data[0] == "STOP_MANUAL":
            proto.guiComm.type = guiComm_pb2.STOP_MANUAL
        elif data[0] == "UPDATE_PIDS":
            proto.guiComm.type = guiComm_pb2.UPDATE_PIDS
            proto.guiComm.jsonMissions = data[1]
        elif data[0] == "FIRE_WEAPONS":
            proto.guiComm.type = guiComm_pb2.FIRE_WEAPONS
            proto.guiComm.fireWeapons1 = data[1]
            proto.guiComm.fireWeapons2 = data[2]
            proto.guiComm.fireWeapons3 = data[3]
            proto.guiComm.fireWeapons4 = data[4]
            proto.guiComm.fireWeapons5 = data[5]
        else:
             _raiseTypeException("{}_{}".format(protoType,data[0]))
    else:
        raise Exception("Unknown protobuf type: {}".format(protoType))
    return proto

def _raiseTypeException(protoType):
    raise Exception("Invalid data format for type: {}".format(protoType))
