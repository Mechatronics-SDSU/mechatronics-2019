import pygame


class Thruster:
    '''
    This class creates objects thrusters. Includes identification numbers and speeds
    of said thrusters. If and when necessary, we can come up with more properties that
    the thruster might include.
    '''
    def __init__(self, number, speed):
        self.number = number
        self.speed = speed

    def set_number (self, number):
        self.number = number

    def get_number(self):
        return self.number

    def set_speed (self, speed):
        self.speed = speed

    def get_speed(self):
        return self.speed

def thrust_speed(value):
    '''
    This function calculates the speed the thruster should have depending on Xbox input
    Designed to go from 0 to 255, like the ESCs
    '''
    return ((value*128) + 128)

#Create a list of the sub's thrusters. Important because we want to map different
#analog sticks and buttons to different thrusters

num_thrusters = 8
thrusters = []
for i in range(0, num_thrusters):
    thruster = Thruster(i, thrust_speed(0))
    thrusters.append(thruster)


pygame.init()


size = [500, 250]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Thruster Test")

#Determine whether or not user is finished with the game
done = False

#Control how fast screen updates
clock = pygame.time.Clock()


#Initialize joysticks
pygame.joystick.init()

while done == False:
    for event in pygame.event.get(): #Basically if the user did something
         if event.type == pygame.QUIT:
             done = True #Stopping condiition to exit this loop. Closes the game

    #Assume we only need one joystick. Don't want multiple people moving the sub
    #simultaneously. That would not be ideal
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    #Get name of the joystick
    name = joystick.get_name()
    print(name)
    #Trying to figure out which axis, button, etc. does what
    num_axes = joystick.get_numaxes()
    print(num_axes)
    num_buttons = joystick.get_numbuttons()
    print(num_buttons)

    #List of axes and buttons. Populating them with all the sticks and buttons
    #available on the Xbox controller
    axes = []
    buttons = []

    for i in range(0, num_axes):
        axis = joystick.get_axis(i)
        print(axis)
        axes.append(axis)

    for i in range(0, num_buttons):
        button = joystick.get_button(i)
        print(button)
        buttons.append(button)

    #This for loop is to get the thruster to send the correct speed depending
    #on the input of the user's control

    for thruster in thrusters:
        #Map thrusters 1 and 7 to the left control stick
        if (thruster.get_number() == 0) or (thruster.get_number() == 6):
            thruster.set_speed(thrust_speed(-1 *(axes[1])))

        #Map thrusters 3 and 5 to the right control stick. Positive/negative
        #inverted for this control stick
        elif (thruster.get_number() == 2) or (thruster.get_number() == 4):
            thruster.set_speed(thrust_speed(-1 *(axes[4])))

        #Map thruster 2 and 6 to the left and right bumper. Left goes left, right
        #goes right. If both are clicked don't actually calculate speed, but output
        #error message, as this would break the thruster
        elif (thruster.get_number() == 1) or (thruster.get_number() == 5):
            if buttons[4] == 1:
                thruster.set_speed(thrust_speed(-1*(buttons[4])))
            elif buttons[5] == 1:
                thruster.set_speed(thrust_speed(buttons[5]))
            else:
                thruster.set_speed(thrust_speed(0))

        #Map thruster 4 and 8 to the left and right trigger. Left goeif buttons[4] and buttons[5] == 1:left goes backward,
        #right goes forward. If both are clicked, again, don't actually calculate
        #speed. Also analog, so they fall under axes for Xbox
        else:
            if axes[2] > 0.00:
                thruster.set_speed(thrust_speed(-1 *(axes[2])))
            elif axes[5] > 0.00:
                thruster.set_speed(thrust_speed(axes[5]))

    for thruster in thrusters:
        print("Thruster %s: %d" %(thruster.get_number(), thruster.get_speed()))

# if A pressed
pygame.quit()
