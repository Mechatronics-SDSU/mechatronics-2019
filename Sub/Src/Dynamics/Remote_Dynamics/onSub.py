import sys
import pickle

sys.path.append("..")
from NodeClass import Node

class sub_node(Node):

    def run(self, port):
        while True:
            arr = self._subscribers[port].serial_subscribe()

def main():
    print_node = sub_node('127.0.0.101', "remote control", 'udp')
    print_node.add_subscriber(5558, 'udp', 0.001)
    print_node.run(5558)

if __name__ == '__main__':
    main()


'''
#!/usr/bin/env python3
import thruster
import nodes
import threading

class ThrusterConfigNode(nodes.nodeBase, threading.Thread):

    def __init__(self):
        super(ThrusterConfigNode,self).__init__(self)
        self._initialize_thrusters()
        self._subscriber=node.nodeBase('127.0.0.101', "UDP", "REMOTE").create_subscriber(5558)

    def _initialize_thrusters(self):
        self._thruster_1=thruster(1);
        self._thruster_2=thruster(2);
        self._thruster_3=thruster(3);
        self._thruster_4=thruster(4);
        self._thruster_5=thruster(5);
        self._thruster_6=thruster(6);
        self._thruster_7=thruster(7);
        self._thruster_8=thruster(8);


    def run(self):
        while True:
            DATA=self._subscriber.subscribe()
            self._thruster_1.setThrust(DATA[0][0])
            self._thruster_2.setThrust(DATA[0][1])
            self._thruster_3.setThrust(DATA[0][2])
            self._thruster_4.setThrust(DATA[0][3])
            self._thruster_5.setThrust(DATA[0][4])
            self._thruster_6.setThrust(DATA[0][5])
            self._thruster_7.setThrust(DATA[0][6])
            self._thruster_8.setThrust(DATA[0][7])
'''
