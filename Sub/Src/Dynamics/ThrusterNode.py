from message_passing.Nodes.node_base import node_base
from thruster import thruster

class ThrusterNode(node_base):
    def __init__(self, memory, ip_router):
        node_base.__init__(self, memory, ip_router)
        self._thruster_1 = thruster(1)
        self._thruster_2 = thruster(2)
        self._thruster_3 = thruster(3)
        self._thruster_4 = thruster(4)
        self._thruster_5 = thruster(5)
        self._thruster_6 = thruster(6)
        self._thruster_7 = thruster(7)
        self._thruster_8 = thruster(8)

        self._MESSAGE

    def _ThrustSet(self, array):
        self._thruster_1.setThrust(array[0])
        self._thruster_2.setThrust(array[1])
        self._thruster_3.setThrust(array[2])
        self._thruster_4.setThrust(array[3])
        self._thruster_5.setThrust(array[4])
        self._thruster_6.setThrust(array[5])
        self._thruster_7.setThrust(array[6])
        self._thruster_8.setThrust(array[7])

    def run(self):
        self._MESSAGE=self._recv('Thrusters')
        self._ThrustSet(self._MESSAGE)
