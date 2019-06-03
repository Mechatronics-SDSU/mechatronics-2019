import socket
import threading

class nodeBase:
    def __init__(self, HOST, TYPE, TOPIC):
#    "def __init__(self, node_name, device_connection, node_connection_port)"
        '''
            PARAMETERS

            -------------------------------------------------------------------------------------------------
        '''

        self._HOST              = HOST
        self._DOMAIN            = socket.AF_INET  #IPV4 ALWAYS
        self._TYPE              = socket.SOCK_DGRAM if (TYPE.lower() =='UDP'.lower()) else socket.SOCK_STREAM
        self._TOPIC             = TOPIC

        self._PUBLISHERS        = {}  # KEY: PORT | VALUE: PUB
        self._SUBSCRIBERS       = {}  # KEY: PORT | VALUE: LIST(SUB)


    def create_publisher(self, PORT):
#   "def (self, topic, pub_port)"
        '''
            PARAMETERS

            -------------------------------------------------------------------------------------------------

            PORT                    : a  Pipe out to the rest of the NODES
        '''

        NEW_PUB = NODE._Publisher( self._HOST,  PORT, self._TOPIC, self._TYPE);

        self._PUBLISHERS[PORT] = NEW_PUB

        return NEW_PUB

    def create_subscriber(self, PORT):
#    "def (self, topic, callback, timeout, sub_port)"

        NEW_SUB = NODE._Subscriber( self._HOST, PORT, self._TOPIC, self._TYPE);

        try:
            self._SUBSCRIBERS[PORT].append(NEW_SUB)

        except KeyError:
            self._SUBSCRIBERS[PORT] = []
            self._SUBSCRIBERS[PORT].append(NEW_SUB)

        return NEW_SUB

#    def spinOnce(self, specific_subscriber=None, timeout):

#        pass;

    class _Publisher:
        def __init__(self, HOST, PORT, TOPIC, TYPE):

            '''
                PARAMETERS

                -------------------------------------------------------------------------------------------------

                HOST                : IP address

                PORT                : PORT where IP will send data

                DOMAIN              : IPV4 or IPV6

                TYPE                : UDP or TCP | SOCK_DGRAM vs SOCK_STREAM
            '''


            self._HOST          = HOST
            self._PORT          = PORT
            self._TOPIC         = TOPIC
            self._DOMAIN        = socket.AF_INET  #IPV4 ALWAYS

            self._TYPE          = TYPE #Inherited from the first part

            self._SOCK          = socket.socket(self._DOMAIN, #internet
                                    self._TYPE) #UDP



        def publish(self, message):

                self._SOCK.sendto( message.encode(), (self._HOST, self._PORT) )


    class _Subscriber:
        def __init__(self, HOST, PORT, TOPIC, TYPE):

            threading.Thread.__init__(self)

            self._HOST          = HOST
            self._PORT          = PORT
            self._TOPIC         = TOPIC

            self._DOMAIN        = socket.AF_INET # IPV4 ALWAYS
            self._TYPE          = TYPE

            self._SOCK          = socket.socket(self._DOMAIN, self._TYPE)

            self._SOCK.bind(( self._HOST, self._PORT ));


        def subscribe(self):
                data, addr = self._SOCK.recvfrom(1024) #buffer size 1024 bytes
                return data;

