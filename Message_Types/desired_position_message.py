'''
'''
import struct

class Desired_Position_Message:
    '''
    '''
    def __init__(self):
        '''
        '''
        #construct the message format
        #6 floats for roll, pitch, yaw, North, East, Depth
        self.message_constructor = 'ffffff'
        #number of bytes for this message
        self.size = 24

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
