#!/usr/bin/env python3

from RemoteNode import RemoteNode
from ThrusterNode import ThrusterNode

Memory={'Thrusters':[[0,0,0,0,0,0,0,0]]}
IP={}

MyThusterNode= ThrusterNode(Memory,IP)
MyRemoteNode = RemoteNode(Memory,IP)

MyThusterNode.start()
MyRemoteNode.start()
