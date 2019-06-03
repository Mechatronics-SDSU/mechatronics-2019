import nodes
import pygame

# Initialization Step
nodeBase=nodes.nodeBase

pygame.init()
pygame.joystick.init()

# Initialize Remote
Remote=pygame.joystick.Joystick(0)
Remote.init()

# initialize Node
remote_node = Node("192.168.1.14","UDP", "Remote Control")

remote_publisher=remote_node.create_publisher(5558)

Calibration_Mode=True;

while True:
    for event in pygame.event.get():
        if Calibrate(event).upper=="SWAP":
            Calibrateion_Mode= not Calibration_Mode;

        if Calibration_Mode:
            remote_publisher.publish(Calibration(event))

        else:
            remote_publisher.publish(Regular(event))
