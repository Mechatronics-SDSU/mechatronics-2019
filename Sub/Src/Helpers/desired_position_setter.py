import sys
import os
PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import desired_position_pb2

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from MechOS import mechos
import time

class CMD_Position_Setter:
    '''
    The CMD Position Setter is a command line tool to be able to send desired
    position and oritientation request to the sub through MechOS.
    '''
    def __init__(self):
        '''
        '''
        self.desired_position_proto = desired_position_pb2.DESIRED_POS()

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Create a MechOS publisher to send desired position data
        self.position_setter_node = mechos.Node("POS_SETTER", configs["ip"])
        self.position_setter_publisher = self.position_setter_node.create_publisher("DP", configs["pub_port"])

    def __choose_operation(self):
        '''
        '''
        print("Please Choose the operation you would like to perform.")
        print("\t-->Set Desired Position (relative to set origin): Press [1]")
        print("\t-->Set Current Position to Origin:                Press [2]")
        setting = input("Selection (or press [E] to exit):")

        if(setting == "E"or setting == 'e'):
            sys.exit()
        elif(int(setting) == 1):
            self.__set_desired_position()


    def __set_desired_position(self):
        '''
        '''
        print("")
        print("\t\tSet Desired Position.")
        print("Please send Position in the order and form of 'roll pitch yaw depth north_pos east_pos'")

        while(True):
            position_str = input("Position (or press [E] to exit):")
            print(position_str)

            if(position_str == "E" or position_str == "e"):
                break

            else:
                desired_position = position_str.split(' ')
                for index, pos in enumerate(desired_position):
                    desired_position[index] = float(pos)

                #Set data into position proto
                self.desired_position_proto.roll  = desired_position[0]
                self.desired_position_proto.pitch = desired_position[1]
                self.desired_position_proto.yaw   = desired_position[2]
                self.desired_position_proto.depth = desired_position[3]
                self.desired_position_proto.north_pos = desired_position[4]
                self.desired_position_proto.east_pos = desired_position[5]

                #Serialze and publish proto position data
                serialized_position = self.desired_position_proto.SerializeToString()
                self.position_setter_publisher.publish(serialized_position)



    def run(self):
        '''
        Continually running loop that lets the user choose options to set the desired
        position and orientation of the sub.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        print("\nWelcome to the CMD Position Setter tool.\n")

        while(True):

            self.__choose_operation()

if __name__ == "__main__":
    position_setter = CMD_Position_Setter()
    position_setter.run()
