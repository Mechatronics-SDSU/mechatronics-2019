'''
SensorHubBase is the parent of all nodes that harvest
sensor data.
'''
class SensorHubBase():

    '''
    SensorHubBase is the parent of all process that harvest/collect data from the
    on-board sensors. For each sensor, a derived class should be defined that draws
    from this classes parameters to structure the how sensor data is collected and
    distributed through the entirety of the system.

    Class to be overriden:
        __init__
        receiveSensorData
    '''
    def __init__(self):
        '''
        The constructor for sensor nodes should be overriden. In the constructor,
        a MechOS node should be defined to emit the sensor data. Also connections
        (such as serial) should be established with the physical sensors.

        Global (parent values) should be initialized.
            type: The type of data that will be sent. Check protobuf for type
                    name.
            data: array that stores sensor output
            publisher: A MechOS publisher object to be overriden in class. This
                        publisher should emit the sensor data.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.type = "NULL"
        self.data = []
        self.publisher = None

    def receiveSensorData(self):
        '''
        This method should be overriden. This method is used to collect the sensor
        data from the system (ex: Use Serial communication to collect IMU data).
        The data should be collected and stored in the global data variable.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        pass

    #TODO View Mechos and learn how to publish
    #TODO Create Protobuf Factory!
    def publishData(self):
        '''
        This method should NOT be overriden. This method takes the sensor data
        stored in the global "data" attribute, packages it with the standard
        protobuf message protocol defined, and publishes the data the the MechOS
        system.

        Parameters:
            N/A

        Returns:
            True: If data was published successfully
            False: Otherwise
        '''
        #Call protobuf factories constrcutProtobuf function
        #publish data

        return False

    def run(self):
        '''
        This method should be overriden. The goal of this method is to run as
        a single process in a script. This method should continually collect sensor
        data from the system and pubhish it to the MechOS system. If any errors
        are encounter, they should be logged.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        while True:
            try:
                self.data = self.receiveData()
                self.publishData()
            except Exception as e:
                print(e) #TODO Actually log the data instead of print!
