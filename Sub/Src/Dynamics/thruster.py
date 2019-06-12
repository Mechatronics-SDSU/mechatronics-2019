from Driver.device import maestro
import numpy as np

class thruster:
    def __init__(self, number=None):
        self._number = number;
        self._servoController=maestro()

    def setThrust(self, thrust):
        '''
        Set a Number between -100, and 100
            :-100 is up
            : 100 is down
        '''
        thrust = int(np.interp(thrust, [-100, 100], [0, 254]))
        self._servoController.set_target(self._number, thrust)
