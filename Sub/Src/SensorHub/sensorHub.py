'''
SensorHubBase is the parent of all nodes that harvest
sensor data.
'''
class SensorHubBase:

    '''
    The constructor should be overridden!
    The goals of the constructor are the following:
     - Establish a connection with Mechos.
     - Setup globals and establisha connection
       with the sensor.
    GLOBALS:
     - type = The type of data that will be sent.
              Check protobuf for type name.
     - data = array that stores sensor output
     - publisher = Mechos publisher, should be
                   overridden in class.
    '''
    def __init__(self):
        self.type = "NULL"
        self.data = []
        self.publisher = None

    '''
    This method should be overridden!
    The goals of the method are as follows:
     - Receive and parse data

    Throws:
     - Exception if there is an issue with sensor data collection

    Returns:
     - Sensor data in the form of an array
    '''
    def receiveData(self):
        return None

    '''
    This method should NOT be overridden!
    The goal of this method is:
     - Package the protobuf
     - Then, publish protobuf

    Throws:
     - Exception if data cannot be published

    Returns:
     - True if data published
     - Otherwise, False
    '''
    #TODO View Mechos and learn how to publish
    #TODO Create Protobuf Factory!
    def publishData(self):
        #Call protobuf factories constrcutProtobuf function
        #publish data
        return False

    '''
    This method should be overridden!
    The goal of this method is:
     - Receive data and publish it as fast as possible
     - Logs issues with receiving or publishing data
    '''
    def run(self):
        return none
