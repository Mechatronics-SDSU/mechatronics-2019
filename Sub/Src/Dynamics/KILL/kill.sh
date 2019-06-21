#!/usr/bin/env python3
import os
import sys
comm_path = os.path.join("..")
sys.path.append(comm_path)

from Driver.device import maestro

MAESTRO=maestro()

MAESTRO.set_target(0,0)
MAESTRO.set_target(1,0)
MAESTRO.set_target(2,0)
MAESTRO.set_target(3,0)
MAESTRO.set_target(4,0)
MAESTRO.set_target(5,0)
MAESTRO.set_target(6,0)
MAESTRO.set_target(7,0)

print('SHOULD BE KILLED')
