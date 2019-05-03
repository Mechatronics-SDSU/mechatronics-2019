import pygame
import numpy as np

def set_thruster_value(thrusters, num, value):
    '''
    This function accesses the speed of every single thruster and changes it accordingly.
    Parameters: List of thrusters, thruster to change (along with sibling thruster), and Xbox input
    Returns: The same thruster list, this time with speeds corresponding to the Xbox input sent
    '''
    if num == 0:
        thrusters[0, 1] = -1 * value
        thrusters[6, 1] = -1 * value
    elif num == 1:
        thrusters[1, 1] = value
        thrusters[5, 1] = value
    elif num == 2:
        thrusters[2, 1] = -1 * value
        thrusters[4, 1] = -1 * value
    elif num == 3:
        thrusters[3, 1] = value
        thrusters[7, 1] = value
    #print(np.array(thrusters[:,1]))
    return np.array(thrusters[:,1])

def Calibrate(thrusters, P, event):
    '''
    The numbers in the loop might seem extremely intimidating, but they are not important
    The axes were derived from trial and error, and may change depending on controller
    The threshold value of 0.3 that you see for axes 2 and 5 are because those are analog
    triggers with a certain "dead zone". They never truly go to -1, which they're supposed
    to do when the triggers are released. That's why I just set the whole thing to zero and
    got rid of thruster power to if we go lower than -0.3. Otherwise, on this current controller,
    axis 1 is the left control stick's vertical movement, axis 2 is the left analog trigger, axis 4
    is the right control stick's vertical movement, and axis 5 is the right analog trigger. Button 4
    is the left bumper, button 5 is the right bumper
    '''
    if event.type == pygame.JOYAXISMOTION:
        if event.axis == 1:
            return set_thruster_value(thrusters, 0, event.value)
        elif event.axis == 2:
              return set_thruster_value(thrusters, 3, (-1*event.value))
        elif event.axis  == 4:
            return set_thruster_value(thrusters, 2, event.value)
        elif event.axis == 5:
            return set_thruster_value(thrusters, 3, event.value)
    elif event.type == pygame.JOYBUTTONDOWN:
        if event.button == 4:
            return set_thruster_value(thrusters, 1, -1)
        elif event.button == 5:
            return set_thruster_value(thrusters, 1 ,1)
        elif event.button == 11:
            return "SWAP"
    elif event.type == pygame.JOYBUTTONUP:
        if event.button == 4:
            return set_thruster_value(thrusters, 1, 0)
        elif event.button == 5:
            return set_thruster_value(thrusters, 1, 0)

def main():
    thrusters = np.matrix([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]])
    clock = pygame.time.Clock()
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    while True:
        for event in pygame.event.get():
            Calibrate(thrusters, event)
            clock.tick(15)

if __name__ == '__main__':
    main()
