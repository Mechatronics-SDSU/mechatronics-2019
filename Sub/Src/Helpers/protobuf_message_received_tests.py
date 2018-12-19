'''
Copyright 2018, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 12/19/2018
Description: This module is used to test proper messages received throught MechOS
using the protobuf message protocol.
'''
import sys
import os
PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)

import argparse
from MechOS import mechos
import time
from protoFactory import packageProtobuf
import Mechatronics_pb2

class MessagePrinter():
    '''
    This class is used to subsribe to a list of MechOS publisher topics and display
    the data.
    '''
    def __init__(self, reg_topics, proto_topics):
        '''
        Initialize the MechOS subscribers to each topic passed in the list of
        topics.

        Parameters:
            reg_topics: A string list of MechOS publisher topics to subscribe to.
                These topics don't get any deserializtion (print them as they are
                received)
            proto_topics: A string list of MechOS topics that use the protoFactory
                        protobufs.

        Returns:
            N/A
        '''
        self.reg_topics = reg_topics
        self.proto_topics = proto_topics
        self.message_printer_node = mechos.Node("MESSAGE_PRINTER")

        #Create a MechOS subcriber for each topic
        if self.reg_topics is not None:
            for topic in self.reg_topics:
                self.message_printer_node.create_subscriber(topic, self.print_reg_message)
        if self.proto_topics is not None:
            for proto_topic in self.proto_topics:
                self.message_printer_node.create_subscriber(proto_topic,
                                                    self.print_proto_message)

    def print_reg_message(self, data):
        '''
        This is the callback function that the subcribers should call and pass data
        to in order to print the data. This data is printed raw as is (not deserialized).

        Parameters:
            data: The data received from a MechOS subscriber to print
        Returns:
            N/A
        '''
        print(data)

    def print_proto_message(self, data):
        '''
        This is the callbackb function that the protoFactroy subcriber topic
        should call and pass the serialized data to in order to be deserialized
        and printed.

        Parameters:
            data: The serialized protobuf data received from the MechOS subsriber
        Returns:
            N/A
        '''
        message_proto = Mechatronics_pb2.Mechatronics()
        message_proto.ParseFromString(data)
        print(message_proto)

    def print_all(self):
        '''
        Print all available data collected by each subscriber for both reg topics
        and proto topics.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.message_printer_node.spinOnce()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--reg_topics", nargs="+", type=str,
                help="Input the MechOS topic names you wish to subscribe to.")
    parser.add_argument("--proto_topics", nargs="+", type=str,
    help="MechOS topics that use the mechatronics protofactory.")

    args = parser.parse_args()
    print(args.proto_topics)
    message_printer = MessagePrinter(args.reg_topics, args.proto_topics)

    while(1):
        message_printer.print_all()
        time.sleep(0.25)
