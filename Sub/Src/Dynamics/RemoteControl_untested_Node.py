import struct
import socket
import pygame
import time
import numpy as np
from message_passing.Nodes.node_base_udp import node_base
import message_passing

class RemoteControlNode(node_base):

    def __init__(self, IP, MEM):
        '''
        This class initializes the Xbox remote control and handles all input
        logic. It inherits functionality from node_base. The idea is to accept
        input from the Xbox control, map it into a thruster matrix, and then
        send that matrix over the network via udp to the address specified by
        the user.

        Parameters:
            IP:A dictionary containing the address and sockets to connect to for
               publish and subscribes
            MEM:Also a dictionary, contains local keys to update. Used for local
                data transfer

        Returns: N/A
        '''

        node_base.__init__(self, MEM, IP)
        pygame.init()   #Disgusting pygame stuff
        pygame.joystick.init()
        self._joystick = pygame.joystick.Joystick(0)
        self._joystick.init()
        #self._num_axes = self._joystick.get_numaxes()
        #print(self._num_axes)
        self._axes = [0, 0, 0, 0, 0, 0]
        self.axis0 = 0
        self.axis1 = 0
        self.axis2 = 0
        self.axis3 = 0
        self.axis4 = 0
        self.axis5 = 0
        self._memory = MEM  #Standard getters/setters for network and local
        self._ip_route = IP
        self._matrix = np.array([[1,0,0,0,0,0,0,0],
                                 [0,0,1,0,0,0,0,0],
                                 [0,0,0,0,1,0,0,0],
                                 [0,0,0,0,0,0,1,0],
                                 [0,1,0,0,0,0,0,0],
                                 [0,0,0,1,0,0,0,0],
                                 [0,0,0,0,0,1,0,0],
                                 [0,0,0,0,0,0,0,1]])

    def _thruster_activation(self, axis):

        thruster_array=np.array([[1,-1,1,-1]])

        if np.any(axis[2]):
            return -1*thruster_array*axis[2]

        else: #axis[5]:
            return thruster_array*axis[5]

        #Will Still be Zero if Zero

    def _joystick_right(self,axis):
        x=round(axis[3],3)
        y=round(axis[4],3)

        y0=.2*abs(y)
        x0=.2*abs(x)
        thruster_ceiling_y =abs(y)+y0 if (abs(y)+y0 <  1) else abs(y)
        thruster_floor_y   =abs(y)-y0 if (abs(y)-y0 >  0) else abs(y)

        thruster_ceiling_x =abs(x)+x0 if (abs(x)+x0 <  1) else abs(x)
        thruster_floor_x   =abs(x)-x0 if (abs(x)-x0 >  0) else abs(x)

        if y >= .4:
            if (-.4 < x) and (x <.4):
                #Forward
                return abs(np.array([[thruster_ceiling_y, thruster_ceiling_y, thruster_floor_y, thruster_floor_y]]))

            elif (x < -.4):
                #Forward Left
                return abs(np.array([[thruster_ceiling_y, y, y, thruster_floor_y]]))

            elif (x > .4):
                #Forward Right
                return abs(np.array([[y, thruster_ceiling_y, thruster_floor_y, y]]))

        elif y <= -.4:
            if (-.4 < x) and (x < .4):
                #Backward
                return abs(np.array([[thruster_floor_y, thruster_floor_y, thruster_ceiling_y, thruster_ceiling_y]]))

            elif (x < -.4):
                #Backward Left
                return abs(np.array([[thruster_floor_y, y, y, thruster_ceiling_y]]))

            elif (x > .4):
                #Backward Right
                return abs(np.array([[y, thruster_floor_y, thruster_ceiling_y, y]]))

        else: #-.4 < y < .4
            if (x > .1):
                #Right
                return abs(np.array([[thruster_floor_x ,thruster_ceiling_x, thruster_floor_x, thruster_ceiling_x ]]))
            elif (x < -.1):
                #Left
                return abs(np.array([[thruster_ceiling_x, thruster_floor_x, thruster_ceiling_x, thruster_floor_x ]]))
            else:
                return np.array([[0,0,0,0]])

    def _joystick_left(self, axis):
        x=round(axis[0], 3) #round to 10^-3 digits
        y=round(axis[1], 3) #round to 10^-3 digits

        y0=.2*abs(y)
        x0=.2*abs(x)

        return np.array([[-1*x, 1*y,-1*x, -1*y]])


    def Remote_Command(self, array_axis):
        '''
        Remomte Commands to Control Flow of Events
        '''
        odd_thrusters     = self._thruster_activation(array_axis)
        odd_thrusters_mod = self._joystick_right(array_axis)
        even_thrusters    = self._joystick_left(array_axis)


        if np.any(odd_thrusters_mod):
            return np.concatenate((odd_thrusters*odd_thrusters_mod, even_thrusters), axis=1)

        else:
            return np.concatenate((odd_thrusters, even_thrusters), axis=1)



    def run(self):
        '''
        Continuously send Xbox data over the network specified
        Parameters:
            N/A
        Returns:
            N/A
        '''
        while True:
            if pygame.event.peek():

                event=pygame.event.poll()

                if event.type==pygame.JOYAXISMOTION:
                    if event.axis==0:
                        self.axis0=round(event.value, 3)

                    if event.axis==1:
                        #Flip Axis 1 for Unit Circle Qualities
                        self.axis1= -1*round(event.value, 3)

                    if event.axis==2:
                        self.axis2=round(abs((event.value + 1)/2 ), 3)

                    if event.axis==3:
                        self.axis3=round(event.value, 3)

                    if event.axis==4:
                        #Flip Axis 4 for Unit Circle Qualities
                        self.axis4= -1*round(event.value, 3)

                    if event.axis==5:
                        self.axis5=round(abs((event.value + 1)/2 ), 3)

                else:
                   self.axis0,self.axis1,self.axis2,self.axis3,self.axis4,self.axis5 = (0,0,0,0,0,0)

                axis_array=[self.axis0, self.axis1, self.axis2, self.axis3, self.axis4, self.axis5]
                dot_matrix = np.dot(self.Remote_Command(axis_array), self._matrix)
                print(dot_matrix)

                byte_matrix = struct.pack('ffffffff',dot_matrix[0][0],
                                                     dot_matrix[0][1],
                                                     dot_matrix[0][2],
                                                     dot_matrix[0][3],
                                                     dot_matrix[0][4],
                                                     dot_matrix[0][5],
                                                     dot_matrix[0][6],
                                                     dot_matrix[0][7])


                self._send(msg=(byte_matrix), register='RC', local=False, foreign=True)
                print(byte_matrix)
            else:
                time.sleep(0)


if __name__ == '__main__':
    rc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thrust_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ('192.168.1.14', 5558)

    IP={'RC':
            {
            'address': ip_address,
            'sockets': (rc_socket, thrust_socket),
            'type': 'UDP'
            }
        }
    MEM={'RC':b'\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00\x00\x01\x807\x00\x00\x00\x00'}
    remote_node = RemoteControlNode(IP, MEM)
    remote_node.start()
