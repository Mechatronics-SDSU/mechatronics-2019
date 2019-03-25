'''
Adapted from the origional dvl.py by Jared Guerrero, and in Accordance with Mechatronics Etiquite and
the Creative Commons Licence LLC.

Current Maintainers: Christian Gould and Cole Brower
Email: Christian.d.gould@gmail.com
Last Modified 1/29/2019
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

class DVL_Data_Driver:
	def __init__(self, comport):
		self.DVLCom = serial.Serial(comport, 115200, timeout=1)

	def Get_Velocity(self):
	'''
		The DVL has been setup to be cyclic, wherupon the Headerbye 'sync' is used to determine where the string restarts

		#important Variable Descriptions#
		-----------
		SYNC -- Determines the sync byte to determine the system
		ID -- Determines the type of Data that will be Sent as a stream: Note that this is changeable

		SEE: DVL integrators Guide from NORTEC There is one Freely avaliable online, (it's on a git)

		The Velocities must be unpacked from a set of four bytes, as it is packed in a C struct
		NOTE: the C struct module 'struct' in python will unwrap these bytes into a tuple
		Be sure to index this to get the data inside the touple to be consistent with Protobuf binaries
	'''
		SYNC = 0;
		while(SYNC != "0xa5"):
			SYNC = hex(ord(self.DVLCom.read()))
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
		return velZ[0], velX[0], velY[0], error[0]

class DVL_Publisher(SensorHubBase):
	'''
	Communicates with the Nortek DVL and publishes Data to sensor hub to be routed to mission planner
	and movement control
	'''

	def __init__(self,comport):

		super(DVL_Publisher,self).__init__()
		#Change type to match protobuf type
		self.type = "DVL_DATA"

		#Create an Object for Nortec DVL data
		self.DVL  = DVL_Data_Driver(comport);

		#Define a MechOS node and publisher
		self.sensorHub_DVL = mechos.Node("SENSORHUB_DVL")

		#Override the parent publisher attribute
		self.publisher = self.sensorHub_DVL.create_publisher("DVL_DATA")

	def Velocity_TO_Displacement(self):
		'''
		Converts Velocity Data to Displacement data as Components: Dx,Dy,Dz
		'''
		'''
			To be implemented with new protobuf
		'''
		pass;


	def publish(self):
		'''
		Publishes Velocity Data to the SensorHub SuperClass via the "publish_data" function
		'''
		while(1):
			Z, X, Y, err = self.DVL.Get_Velocity()
			self.data = [float(x) for x in [Z,X,Y,err]]
			if( v_t != 0 for v_t in self.data):
				self.publish_data()
				#print(self.data) # useful for Debugging
			time.sleep(0.25)


if __name__ == "__main__":
	# this is simply a listener to the Port, Please Change your port Accordingly
	DVL = DVL_Publisher('/dev/ttyUSB0');
	DVL.publish()
