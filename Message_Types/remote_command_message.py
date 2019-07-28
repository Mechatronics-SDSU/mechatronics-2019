'''
'''
import struct

class Remote_Command_Message:
    '''
    '''
    def __init__(self):
        '''
        '''
        #construct the message format
        #4 floats for the movement in yaw, x direction, y direction, and depth
        #3 bools for zero position, record waypoint, and hold depth
        self.message_constructor = 'ffff???'
        #number of bytes for this message
        self.size = 19

    def _pack(self, message):
        '''
        '''
        encoded_message = struct.pack(self.message_constructor, *message)
        return(encoded_message)

    def _unpack(self, encoded_message):
        '''
        '''
        message = struct.unpack(self.message_constructor, encoded_message)
        return(message)
