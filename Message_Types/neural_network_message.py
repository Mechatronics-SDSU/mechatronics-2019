'''
'''
import struct

class Neural_Network_Message:
    '''
    '''
    def __init__(self):

        self.message_constructor = 'sfffffffffff'
        self.size = 52

    def _pack(self, message):
        '''
        '''
        encoded_message = struct.pack(self.message_constructor, *message)
        return(encoded_message)

    def _unpack(self, encoded_message):
        message = struct.unpack(self.message_constructor, encoded_message)
        return(message)
