import socket
import threading
import time as CLOCK

class Publisher:
    def __init__(self, HOST, PORT, TOPIC, PUBRATE=None):
#        super(Publisher, self).__init__(name=TOPIC);

        '''
            PARAMETERS

            -------------------------------------------------------------------------------------------------

            HOST                : IP address

            PORT                : PORT where IP will send data

            DOMAIN              : IPV4 or IPV6

            TYPE                : UDP or TCP | SOCK_DGRAM vs SOCK_STREAM
        '''

        # Networking Utilities
        self._HOST              = HOST
        self._PORT              = PORT
        self._TYPE              = socket.SOCK_DGRAM; # Auto UDP: Unless Specified
        self._DOMAIN            = socket.AF_INET  #IPV4 ALWAYS
        self._TOPIC             = TOPIC #Inherited from the first part
        self._SOCK              = socket.socket(self._DOMAIN, #internet
                                    self._TYPE) #UDP

        self._pubRate           = PUBRATE if (PUBRATE is not None) else .001

        # PubSpecific Utilities
        # Conditions for Threading with While Loops
        # self.paused_condition   = threading.Condition(threading.Lock());
        # self.paused             = False
        self._message           = "Uninitialized";
        self._timeAtLastPublish = None

    def setPubRate(self, RATE): #set the PubRate in Seconds (can also be decimal value)
        self._pubRate=RATE;

    def setType(self, TYPE):
        self._TYPE = socket.SOCK_DGRAM if (TYPE.lower() =='UDP'.lower()) else socket.SOCK_STREAM

    def setMessage(self, message):
        self._message = message;

    #@overloadedMethod
    def publish(self, message=None):
        if message is None:
            self._SOCK.sendto( self._message.encode(), (self._HOST, self._PORT) )

        else:
            self._SOCK.sendto( message.encode(), (self._HOST, self._PORT) )

        self._timeAtLastPublish = CLOCK.time()



    '''# Functionality Should there Be a While loop and no Main Thread
    def pause(self):
        self.paused = True
        self.paused_condition.acquire()

    def resume(self):
        self.paused = False
        self.paused_condition.notify()
        self.paused_condition.release()
    '''

#    def run(self):
#        while(True):
#            with self.paused_condition:
#                while self.paused:
#                    self.paused_condition.wait()
#        self.publish()
