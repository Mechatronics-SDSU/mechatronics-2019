#!/usr/bin/env python3
import os
import sys
comm_path = os.path.join("..")
sys.path.append(comm_path)

from Driver.device import maestro

MAESTRO=maestro()

MAESTRO.set_target(1,127)
MAESTRO.set_target(2,127)
MAESTRO.set_target(3,127)
MAESTRO.set_target(4,127)
MAESTRO.set_target(5,127)
MAESTRO.set_target(6,127)
MAESTRO.set_target(7,127)
MAESTRO.set_target(8,127)

print('SHOULD BE KILLED')
