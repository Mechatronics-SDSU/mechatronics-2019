import struct
import socket
import time
import numpy as np
from message_passing.Nodes.node_base_udp import node_base
import message_passing
from Driver.device import maestro

class ThrusterNode(node_base):

    def __init__(self, IP, MEM):
        '''
        This class initializes the sub's thrusters. Also inherits from
        node_base. Accepts the input from the Xbox, and maps them to the correct
        thruster on the sub
        '''
        node_base.__init__(self, MEM, IP)
        self._memory = MEM
        self._ip_route = IP
        self._maestro = maestro()
        self._message = None

    def _set_thrust(self, array):
        '''
        Take the accepted/received array, use the maestro to map to each
        individual thruster. Only go from 0 to 204, so the PWMs never send more
        than 80 percent power to the thrusters
        Parameters:
            array: The array that we receive from from subsriber end. Write each
            thruster using the maestro
        Returns:
            N/A
        '''
        self._maestro.set_target(1, int(np.interp(array[0], [-1,1], [50,203])))
        self._maestro.set_target(2, int(np.interp(array[1], [-1,1], [82,171])))
        self._maestro.set_target(3, int(np.interp(array[2], [-1,1], [50,203])))
        self._maestro.set_target(4, int(np.interp(array[3], [-1,1], [82,171])))
        self._maestro.set_target(5, int(np.interp(array[4], [-1,1], [50,203])))
        self._maestro.set_target(6, int(np.interp(array[5], [-1,1], [82,171])))
        self._maestro.set_target(7, int(np.interp(array[6], [-1,1], [50,203])))
        self._maestro.set_target(8, int(np.interp(array[7], [-1,1], [82,171])))


    def run(self):
        '''
        Continuonly accept messages, set the thrust.
        Parameters:
            N/A
        Returns:
            N/A
        '''
        while True:
            self._message = self._recv('RC', local = False)
            #print(self._message)
            real_matrix= struct.unpack('ffffffff', self._message)
            #print(real_matrix)
            self._set_thrust(real_matrix)

if __name__ == '__main__':
    rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('192.168.1.14', 5558)

    thrust_socket.bind((ip_address))

    IP={'RC':
            {
            'address': ip_address,
            'sockets': (rc_socket, thrust_socket),
            'type': 'UDP'
            }
        }
    MEM={'RC':b'\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00'}

    thrust_node = ThrusterNode(IP, MEM)
    thrust_node.start()
