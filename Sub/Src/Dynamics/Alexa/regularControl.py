'''
Copyright 2018, Alexa Becerra, All rights reserved
Author: Alexa Becerra <alexa.becerra99@gmail.com>
Description: Regular controls for thruster values.
'''

import pygame
import numpy


def main():
    clock = pygame.time.Clock()
    pygame.init()
    pygame.joystick.init()
    controller = pygame.joystick.Joystick(0)
    controller.init()
    while True:
        for event in pygame.event.get():
            print(Regular(event)[0])
            #clock.tick(15)

def Regular(XBOX_INPUT):
    '''
    Handles values for thuster control of yaw, pitch and roll motions.

    Parameters:
        XBOX_INPUT: A pygame event
    Returns:
        NumPy array with values of all 8 thrusters.
    '''
    if XBOX_INPUT.type == pygame.JOYAXISMOTION:
        InputArray = [0, 0, 0, 0]
        #left stick: x-axis
        if XBOX_INPUT.axis == 0:
            InputArray = numpy.array([XBOX_INPUT.value , 0, 0, 0, 0, 0])
            return dotProduct(InputArray)
        #left stick: y-axis
        if XBOX_INPUT.axis == 1:
            InputArray = numpy.array([0, XBOX_INPUT.value , 0, 0, 0, 0])
            return dotProduct(InputArray)
        #right stick: x-axis
        if XBOX_INPUT.axis == 2:
            InputArray = numpy.array([0, 0 , XBOX_INPUT.value, 0, 0, 0])
            return dotProduct(InputArray)
        #right stick: y-axis
        if XBOX_INPUT.axis == 3:
            InputArray = numpy.array([0, 0 , 0, XBOX_INPUT.value, 0, 0])
            return dotProduct(InputArray)
        #left trigger
        if XBOX_INPUT.axis == 4:
            XBOX_INPUT.value = (XBOX_INPUT.value + 1)/2
            InputArray = numpy.array([0, 0 , 0, 0, XBOX_INPUT.value, 0])
            return dotProduct(InputArray)
        #right trigger
        if XBOX_INPUT.axis == 5:
            XBOX_INPUT.value = (XBOX_INPUT.value + 1)/2
            InputArray = numpy.array([0, 0 , 0, 0, 0, XBOX_INPUT.value])
            return dotProduct(InputArray)
    elif XBOX_INPUT.type == pygame.JOYBUTTONDOWN:
        if XBOX_INPUT.button == 1:
            return "Swap"

def dotProduct(Input):
    '''
    Performs dot product of the thurster matrix to axis array.

    Parameters:
        Input: Numpy array with axis values
    Return:
        Numpy array with thruster values
    '''
    ThrusterMatrix = numpy.matrix(\
    '0 1 0 0 0 1 0 0 ; \
    0 0 0 -1 0 0 0 -1 ; \
    1 0 1 0 1 0 1 0 ; \
    -1 0 -1 0 -1 0 -1 0; \
    0 -1 0 0 0 1 0 0; \
    0 1 0 0 0 -1 0 0')
    XBOX_OUTPUT = numpy.dot(Input,ThrusterMatrix)
#   print(XBOX_OUTPUT)
    return XBOX_OUTPUT

if __name__ == '__main__':
    main()
