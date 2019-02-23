import pygame
import time

INACTIVITY_RECONNECT_TIME = 5
RECONNECT_TIMEOUT = 1

class ControllerInput():
    def __init__(self):
        pygame.joystick.init()
        self.lastTime = 0
        self.lastActive = 0

    def hasController(self):
        ''' Checks connection status based on time difference and properties provided by pygame
            Parameters:
                N/A
            Returns:
                Integer count of connected controllers
            '''
        now = time.time()
        if now - self.lastActive > INACTIVITY_RECONNECT_TIME and now - self.lastTime > RECONNECT_TIMEOUT:
            self.lastTime = now
            pygame.joystick.quit()
            pygame.joystick.init()
        return pygame.joystick.get_count() > 0

#for testing only
if __name__ == "__main__":
    import sys
    controller = ControllerInput()
    while(1):
        if not controller.hasController():
            print ("reconnect")
        else:
            print("connected")

    sys.exit(app.exec_())

