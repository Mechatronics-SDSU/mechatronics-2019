from Nodes.node_base import node_base
import pygame

class RemoteControlNode(node_base):
    def __init__(self):
        super(RemoteControlNode,self).__init__()
        print(__class__.__name__,'says hello!')

    def run(self):
        print(__class__.__name__, 'Running')


if __name__=='__main__':
    import sys
    MyRemote=RemoteControlNode()
    MyRemote.start()
    print('Exiting...')
    sys.exit(0)
