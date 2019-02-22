import pygame
import numpy as np
import scipy

#2D matrix of thrusters with respective speed values currently set
thrusters = np.matrix([[0, 128], [1, 128], [2, 128], [3, 128], [4, 128], [5, 128], [6, 128], [7, 128]])
P = 2

def thrust_speed(value):
    '''
    This function calculates the speed the thruster should have depending on Xbox input
    Designed to go from 0 to 255, like the ESCs
    '''
    return ((value*128) + 128)

def calibrate(thrusters, num, value):
    '''
    This function accesses the speed of every single thruster and changes it accordingly.
    Parameters: List of thrusters, thruster to change (along with sibling thruster), and Xbox input
    Returns: The same thruster list, this time with speeds corresponding to the Xbox input sent
    '''
    if num == 0:
        thrusters[0, 1] = thrust_speed(-1 * value)
        thrusters[6, 1] = thrust_speed(-1 * value)
    elif num == 1:
        thrusters[1, 1] = thrust_speed(value)
        thrusters[5, 1] = thrust_speed(value)
    elif num == 2:
        thrusters[2, 1] = thrust_speed(-1 * value)
        thrusters[4, 1] = thrust_speed(-1 * value)
    elif num == 3:
        thrusters[3, 1] = thrust_speed(value)
        thrusters[7, 1] = thrust_speed(value)
    return thrusters

pygame.init()
size = [500, 250]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Thruster Test")
done = False
clock = pygame.time.Clock()
pygame.joystick.init()

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
while done == False:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
             done = True
         elif event.type == pygame.JOYAXISMOTION:
             if event.axis == 1:
                 thrusters = calibrate(thrusters, 0, round(event.value, P))
             elif event.axis == 2:
                 if event.value > -0.3:
                    thrusters = calibrate(thrusters, 3, (-1*(round(event.value, P))))
                 else:
                    thrusters = calibrate(thrusters, 3, 0)
             elif event.axis  == 4:
                 thrusters = calibrate(thrusters, 2, round(event.value,P))
             elif event.axis == 5:
                 if event.value > -0.3:
                    thrusters = calibrate(thrusters, 3, round(event.value,P))
                 else:
                    thrusters = calibrate(thrusters, 3, 0)
         elif event.type == pygame.JOYBUTTONDOWN:
             if event.button == 4:
                 thrusters = calibrate(thrusters, 1, -1)
             elif event.button == 5:
                 thrusters = calibrate(thrusters, 1 ,1)
         elif event.type == pygame.JOYBUTTONUP:
             if event.button == 4:
                 thrusters = calibrate(thrusters, 1, 0)
             elif event.button == 5:
                 thrusters = calibrate(thrusters, 1, 0)
    print(thrusters)
pygame.quit()
