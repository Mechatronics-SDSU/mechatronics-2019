import pygame
import numpy as np

def set_thruster_value(input_matrix):
    '''
    Parameters: Matrix of xbox inputs
    Returns: the dot product of the xbox input along with this mathematically
    predetermined map by me, not by Christian at all. Why do you ask?
    '''
    thruster_matrix = np.matrix(\
    '1 0 0 0 0 0 1 0; \
    0 -1 0 0 0 -1 0 0; \
    0 0 0 -1 0 0 0 -1; \
    0 0 1 0 1 0 0 0; \
    0 1 0 0 0 1 0 0; \
    0 0 0 1 0 0 0 1')

    #print(np.dot(input_matrix, thruster_matrix))
    return np.dot(input_matrix, thruster_matrix)

def Calibrate(event):
    '''
    Parameters: Xbox event
    Returns: Dot product of xbox values corresponding to the correct thruster
    '''
    if event.type == pygame.JOYAXISMOTION:
        if event.axis == 1:
            return set_thruster_value(np.array([(-1 *event.value), 0, 0, 0, 0, 0])) #up down on left joystick, inverted
        elif event.axis == 2:
            #xbox trigger initial state is set to 1. this will cause the motors to continue spinning if trigger is released
            return set_thruster_value(np.array([0, 0, ((event.value + 1)/2), 0, 0, 0])) #left trigger
        elif event.axis  == 4:
            return set_thruster_value(np.array([0, 0, 0, (-1 *event.value), 0, 0])) #up/down on right joystick
        elif event.axis == 5:
            #same reason as the left trigger
            return set_thruster_value(np.array([0, 0, 0, 0, 0, ((event.value + 1)/2)])) #right trigger
        else:
            return set_thruster_value(np.array([0,0,0,0,0,0]))

    elif event.type == pygame.JOYBUTTONDOWN:
        if event.button == 4:
            return set_thruster_value(np.array([0, 1, 0, 0, 0, 0])) #left bumper
        elif event.button == 5:
            return set_thruster_value(np.array([0, 0, 0, 0, 1, 0])) #right bumper
        elif event.button == 1:
            return "SWAP"
        else:
            return set_thruster_value(np.array([0,0,0,0,0,0]))
    elif event.type == pygame.JOYBUTTONUP:
        return set_thruster_value(np.array([0,0,0,0,0,0]))

def main():
    clock = pygame.time.Clock()
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    while True:
        for event in pygame.event.get():
            print(Calibrate(event))
            clock.tick(15)

if __name__ == '__main__':
    main()
