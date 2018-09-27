from sensorHub import SensorHubBase

class AHRS(SensorHubBase):

    def __init__(self):
        super(AHRS, self).__init__()
        #Change type to match protobuf type
        self.type = "AHRS_DATA"
        #Establish connection with sensor

    #TODO
    def receiveData(self):
        pass

if __name__ == "__main__":
    ahrs = AHRS()
    print(ahrs.type)
