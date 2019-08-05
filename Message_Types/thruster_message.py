'''
'''
import struct

class Thruster_Message:
    '''
    '''
    def __init__(self):
        '''
        '''
        #construct the message format
        #8 integers for the values to give each thruster
        self.message_constructor = 'iiiiiiii'
        #number of bytes for this message
        self.size = 32

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
