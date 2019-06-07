import socket
import threading
import time as CLOCK
import pickle

class Subscriber:
    def __init__(self, HOST, PORT, TOPIC, SUBRATE=None):

#        super(Subscriber, self).__init__(name=TOPIC);

        self._HOST          = HOST
        self._PORT          = PORT
        self._TOPIC         = TOPIC
        self._DOMAIN        = socket.AF_INET # IPV4 ALWAYS
        self._TYPE          = socket.SOCK_DGRAM # Auto UDP settings
        self._SOCK          = socket.socket(self._DOMAIN, self._TYPE)
        self._SOCK.bind(( self._HOST, self._PORT ))

        self._timeAtLastSubscribe = None;
        self._subRate       = SUBRATE if(SUBRATE is not None) else .001

    def setType(self,TYPE):
        self._TYPE = socket.SOCK_DGRAM if (TYPE.lower() =='UDP'.lower()) else socket.SOCK_STREAM

    def subscribe(self):
        data, addr = self._SOCK.recvfrom(4096) #buffer size 1024 bytes
        self._timeAtLastSubscribe = CLOCK.time()
        print(data.decode())
        #return data.decode()

    def serial_subscribe(self):
        data, addr = self._SOCK.recvfrom(4096)
        print(data)
        #return data

#    def run(self):
#        self.subscribe()
