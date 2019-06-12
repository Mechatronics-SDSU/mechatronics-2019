from message_passing.Nodes.node_base import node_base
from thruster import thruster
from Driver.device import maestro
import struct
import numpy as np

class ThrusterNode(node_base):
    def __init__(self, memory, ip_router):
        node_base.__init__(self, memory, ip_router)
        self.Maestro = maestro()
        '''
        self._thruster_1 = thruster(1)
        self._thruster_2 = thruster(2)
        self._thruster_3 = thruster(3)
        self._thruster_4 = thruster(4)
        self._thruster_5 = thruster(5)
        self._thruster_6 = thruster(6)
        self._thruster_7 = thruster(7)
        self._thruster_8 = thruster(8)
        '''

        self._MESSAGE = [0, 0, 0, 0, 0, 0, 0, 0]

    def _ThrustSet(self, array):

        self.Maestro.set_target(1, int(np.interp(array[0][0], [-1, 1], [0, 254])))
        self.Maestro.set_target(2, int(np.interp(array[0][1], [-1, 1], [0, 254])))
        self.Maestro.set_target(3, int(np.interp(array[0][2], [-1, 1], [0, 254])))
        self.Maestro.set_target(4, int(np.interp(array[0][3], [-1, 1], [0, 254])))
        self.Maestro.set_target(5, int(np.interp(array[0][4], [-1, 1], [0, 254])))
        self.Maestro.set_target(6, int(np.interp(array[0][5], [-1, 1], [0, 254])))
        self.Maestro.set_target(7, int(np.interp(array[0][6], [-1, 1], [0, 254])))
        self.Maestro.set_target(8, int(np.interp(array[0][7], [-1, 1], [0, 254])))

        '''
        self._thruster_1.setThrust(array[0][0])
        self._thruster_2.setThrust(array[0][1])
        self._thruster_3.setThrust(array[0][2])
        self._thruster_4.setThrust(array[0][3])
        self._thruster_5.setThrust(array[0][4])
        self._thruster_6.setThrust(array[0][5])
        self._thruster_7.setThrust(array[0][6])
        self._thruster_8.setThrust(array[0][7])
        '''
    def run(self):
        self._MESSAGE =self._recv('Thrusters')
        print(self._MESSAGE)
        self._ThrustSet(self._MESSAGE)
