import os
import sys
comm_path = os.path.join("..")
sys.path.append(comm_path)

import time
import threading
import socket

from communicationUtils import local as local
from communicationUtils import network as network
from abc import ABC, abstractmethod


class node_base(ABC, threading.Thread):
    def __init__(self, volatile_memory, ip_route ):
        threading.Thread.__init__(self)
        ABC.__init__(self)
        print(__class__.__name__,'inherited')

        self._publisher=network.publisher(ip_route)
        self._subscriber=network.subscriber(ip_route)

        self._reader=local.reader(volatile_memory)
        self._writer=local.writer(volatile_memory)

    def _send(self,  msg, register, local=True, foreign=False):
        '''
            Sends your message to the address(s) provided, either foreign local, or both

            :param byte msg: the message you are sending, could be a byte string
            :param str local_address: a unique key to write to the local volatile_memory
            :param tuple foreign_address: a tuple containing an ip_address and port, pair
            :rtype: int
            :returns: 0 on sucess 1 on error, errors are logged to outputbuffer
        '''


        if foreign:
            self._publisher.publish(msg, register)
            if not local:
                return 0


        return self._writer.write(msg, register)


    def _recv(self, register, local=True):
        '''
            Gets your message from the addresses provided, either local or foreign
            :param tuple address: recv from foreign address of type tuple (IP, PORT)
            :param str address: recv from local address as a string to the dictionary 'x_velocity' etc.
        '''
        if not local:
            return self._subscriber.subscribe(register)
        else:
            return self._reader.read(register)

    @abstractmethod
    def run(self):
        pass

if __name__=='__main__':
    import time

    class WriteNode(node_base):
        def __init__(self, IP, MEM):
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.MSG='uninitialized'
            self.baud=.128

        def set_message(self, message):
            self.MSG=message
        def set_baudrate(self, baudrate):
            self.baud=baudrate

        def run(self):
            start_time = time.time()
            while True:
                if ( (time.time() - start_time) >= self.baud ):
                    self._send(msg=self.MSG, register='Encrypted_dat')
                    start_time=time.time()
                else:
                    time.sleep(0)

    class PublishNode(node_base):
        def __init__(self, IP, MEM):
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            '''
            PublisherNode:
            '''
            self.MSG = b'uninitialized'
            self.baud=.128

        def set_message(self, message):
            self.MSG = message
        def set_baudrate(self, baudrate):
            self.baud = baudrate

        def run(self):
            start_time = time.time()
            while True:
                if((time.time() - start_time) >= self.baud):
                    self._send(msg=self.MSG, register='Encrypted_dat', local=False, foreign=True)
                    start_time = time.time()
                else:
                    time.sleep(0)

    class ReadNode(node_base):
        def __init__(self, IP, MEM):
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.baud=.128

        def run(self):
            start_time = time.time()
            while True:
                if ( (time.time() - start_time) >= self.baud ):
                    print(self._recv('Encrypted_dat')) # Local True By Default
                    start_time=time.time()
                else:
                    time.sleep(0)

    class SubscribeNode(node_base):
        def __init__(self, IP, MEM):
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.baud=.105

            '''
            self.address = list(IP)[0]
            print(self._ip_route)
            '''

        def run(self):
            start_time = time.time()
            while True:
                if ((time.time() - start_time) >= self.baud):
                    print(self._recv('Encrypted_dat', local=False))
                    start_time = time.time()
                else:
                    time.sleep(0)

    # Volatile Memory Instances
    pub_socket1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sub_socket1=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    pub_socket2=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sub_socket2=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Dictionary 

    ip_address1 = ('127.0.0.101', 5558)
    ip_address2 = ('127.0.0.101', 5559)

    sub_socket1.bind((ip_address1))
    sub_socket2.bind((ip_address2))
    #Dictionary with key: ip address, value is tuple with publisher/subscriber socket

    IP={'Encrypted_dat':
                {
                 'address':ip_address1,
                 'sockets':(pub_socket1, sub_socket1),
                 'type':'UDP'
                },
	'Doesnt matter':
                {
                 'address':ip_address2,
                 'sockets':(pub_socket2, sub_socket2),
                 'type':'UDP'
                }
        }

    MEM={'Velocity_x':12.01,'Velocity_y':12.02,'Velocity_z':12.03,'Encrypted_dat':'None'}

    # Initialize Node
    MyWriteNode = WriteNode(IP, MEM)
    #print(MyWriteNode._ip_route)
    MyPublishNode = PublishNode(IP, MEM)
    MyReadNode  = ReadNode(IP, MEM)
    MySubscribeNode = SubscribeNode(IP, MEM)
    #print(MyReadNode._ip_route)

    # Start Thread
    MyWriteNode.start()
    MyPublishNode.start()
    MyReadNode.start()
    MySubscribeNode.start()

    MyWriteNode.set_message('OUTPUT A')

    MyPublishNode.set_message(b'OUTPUT B')

