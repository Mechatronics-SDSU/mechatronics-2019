import os
import sys
comm_path = os.path.join("..", "..")
sys.path.append(comm_path)

import time
import threading
import socket

from message_passing.communicationUtils import local as local
from message_passing.communicationUtils import network as network
from abc import ABC, abstractmethod


class node_base(ABC, threading.Thread):
    '''
    Abstract node_base class. The benefits of having this abstract allows for
    numerous options for initializing and running nodes.
    '''
    def __init__(self, volatile_memory, ip_route):
        '''
        Initializes the node. Inherits from theading.Thread along with all of
        Thread's functions, such as start, run, etc.
        Params:
            volatile_memory:The RAM dictionary. We use this for local input and
                            output. Allows reader and writer to do their jobs
            ip_route:The ip dictionary. Contains the address, publisher socket,
                     subscriber socket, and type of connection as information.
                     Allows publisher and subscriber to do their jobs
        '''
        threading.Thread.__init__(self)
        ABC.__init__(self)
        print(__class__.__name__,'inherited')

        self._publisher=network.publisher(ip_route)
        self._subscriber=network.subscriber(ip_route)

        self._reader=local.reader(volatile_memory)
        self._writer=local.writer(volatile_memory)

    def _send(self,  msg, register, local=True, foreign=False):
        '''
        Sends your message to the address(s) provided, either foreign local or
        both
        Parameters:
            msg:The bytes message that we use to write or publish, or both
            register:The key that we want to write to if local is being used.
                     Also gives access to all the socket and udp/tcp information
                     if the network is being used (publishers)
            local:boolean, states whether or not the data should be sent locally
            foreign:boolean, states whether or not the data should be sent over
                    the network
        Returns:
            N/A
        '''

        if foreign:
            self._publisher.publish(msg, register)
            if not local:
                return
        self._writer.write(msg, register)    #I know this is a return
                                                    #statement, but it doesn't
                                                    #do shit. I'm still too
                                                    #scared to delete the return

    def _recv(self, register, local=True):
        '''
            Gets your message from the addresses provided, either local or
            foreign
            Parameters:
                register:The key to do local reads from. Use it to pull
                         whatever data is stored there. If we are subsrcribing,
                         gives us access to the IP address, sockets, etc to
                         perform the subscribe operation
                local:Boolean, states whether or not we receive data locally or
                      over the network
            Returns:
                    The data received, whether read locally or subscribed to via
                    the network
        '''
        if not local:
            return self._subscriber.subscribe(register)
        else:
            return self._reader.read(register)

    @abstractmethod
    def run(self):
        '''
        This method is abstract. Allows the node to perform any function we wish
        whether that is publishes, subscriptions, or even dumb print statements
        '''
        pass

if __name__=='__main__':
    import time
    '''
    Examples of how to instantiate nodes, and use them. You can initialize them
    however you wish provided you use the correct parameters, you can add any
    function you wish for them to have, and you can pass whatever you want in
    run. However, creating the IP dictionary has a specified method to it, as
    publishes and subscribes will not work if that protocol is not maintained.
    '''
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
