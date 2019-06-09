#!/usr/bin/env python3

from RemoteNode import RemoteNode
from ThrusterNode import ThrusterNode

Memory={'Thrusters':None}
IP={}

MyThusterNode= ThrusterNode(Memory,IP)
MyRemoteNode = RemoteNode(Memory,IP)

MyThusterNode.start()
MyRemoteNode.start()
