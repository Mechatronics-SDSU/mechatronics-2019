import socket
import time
import threading

from abc import ABCMeta, abstractmethod
from Networking import Publisher as PubClass
from Networking import Subscriber as SubClass

class Node(object, metaclass=ABCMeta):

    def __init__(self, host, topic, type):
        self._host = host
        self._topic = topic
        self._type = type
        self._domain = socket.AF_INET
        self._publishers = {} #Key: port. Value: publisher
        self._subscribers = {}

    def get_publisher(self, port):
        try:
            return self._publishers[port]
        except KeyError:
            print("Publisher does not exist")

    def get_subscriber(self, port):
        try:
            return self._subscribers[port]
        except KeyError:
            print("Publisher does not exist")

    def add_publisher(self, port, type = None, pubrate = None):
        self._publishers[port] = PubClass.Publisher(self._host, port, self._topic, pubrate)
        if type is not None:
            self._publishers[port].setType(type)

    def add_subscriber(self, port, type = None, subrate = None):
        self._subscribers[port] = SubClass.Subscriber(self._host, port, self._topic, subrate)
        if type is not None:
            self._subscribers[port].setType(type)

    def delete_publisher(self, port):
        del self._publishers[port]

    def delete_subscriber(self, port):
        del self._subscribers[port]

    @abstractmethod
    def run(self):
        '''
        This is the run method the nodes are going to use. Each of them has the potential to be different, and as such,
        we want to be able to change their run method at moment's notice
        '''
