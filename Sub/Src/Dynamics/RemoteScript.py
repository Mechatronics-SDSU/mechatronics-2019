#!/usr/bin/env python3
import socket
from RemoteNode import RemoteNode
from ThrusterNode import ThrusterNode

if __name__ == '__main__':
    rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('127.0.0.101', 5558)

    thrust_socket.bind((ip_address))

    IP={'RC':
            {
            'address': ip_address,
            'sockets': (rc_socket, thrust_socket),
            'type': 'UDP'
            }
        }
    MEM={'RC':b'\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00'}
    remote_node = RemoteControlNode(IP, MEM)
    thrust_node = ThrusterNode(IP, MEM)

    remote_node.start()
    thrust_node.start()
