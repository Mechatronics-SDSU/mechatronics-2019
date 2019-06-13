import os
import sys
comm_path = os.path.join("..")
sys.path.append(comm_path)

import time
import threading

from communicationUtils import local as local
from communicationUtils import network as network
from abc import ABC, abstractmethod


class node_base(ABC, threading.Thread):
    def __init__(self, volatile_memory, ip_route ):
        threading.Thread.__init__(self)
        ABC.__init__(self)
        print(__class__.__name__,'inherited')

        self._publisher=network.publisher(ip_route, 'UDP')
        self._subscriber=network.subscriber(ip_route, 'UDP')

        self._reader=local.reader(volatile_memory)
        self._writer=local.writer(volatile_memory)

    def _send(self, msg, local_address, foreign_address=None):
        '''
            Sends your message to the address(s) provided, either foreign local, or both

            :param byte msg: the message you are sending, could be a byte string
            :param str local_address: a unique key to write to the local volatile_memory
            :param tuple foreign_address: a tuple containing an ip_address and port, pair
            :rtype: int
            :returns: 0 on sucess 1 on error, errors are logged to outputbuffer
        '''

        if foreign_address is not None:
            self._publisher.publish(msg, foreign_address)

        self._writer.write(local_address, msg)

        return 0;

    def _recv(self, address, local=True):
        '''
            Gets your message from the addresses provided, either local or foreign
            :param tuple address: recv from foreign address of type tuple (IP, PORT)
            :param str address: recv from local address as a string to the dictionary 'x_velocity' etc.
        '''
        if not local:
            return self._subscriber.subscribe(address)
        else:
            return self._reader.read(address)

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
                    self._send(local_address='Encrypted_dat', msg = self.MSG)
                    start_time=time.time()
                else:
                    time.sleep(0)

    class PublishNode(node_base):
        def __init__(self, IP, MEM):
            node_base.__init__(self, MEM, IP)
            self._memory = MEM
            self._ip_route = IP
            self.address = list(IP)[0]
            print(self._ip_route)
            self.MSG = 'uninitialized'
            self.baud=.128

        def set_message(self, message):
            self.MSG = message
        def set_baudrate(self, baudrate):
            self.baud = baudrate

        def run(self):
            start_time = time.time()
            while True:
                if((time.time() - start_time) >= self.baud):
                    self._send(msg=self.MSG, local_address = 'Doesnt matter', foreign_address = IP)
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
            self.baud=.128
            self.address = list(IP)[0]
            print(self._ip_route)

        def run(self):
            start_time = time.time()
            while True:
                if ((time.time() - start_time) >= self.baud):
                    print(self._recv(IP, local=False))
                    start_time = time.time()
                else:
                    time.sleep(0)

    # Volatile Memory Instances
    IP={'127.0.0.101':5558}
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

    MyWriteNode.set_message('Testing Message...initialized')
    MyPublishNode.set_message('This is also a testing message')
