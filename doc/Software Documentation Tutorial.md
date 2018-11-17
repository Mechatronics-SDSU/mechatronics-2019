# Software Documentation Tutorial

### Motivation

When working on a team software project, it is pivotal to provide descriptive and informative documentation of the software you write. Proper documentation increases the overall efficiency of large scale and long term software projects. Remember...you are not the only one reading your code and your code may past down to future software engineers.

## How to Inline Document your Code

It is important as team that we subscribe to a standard form of inline code documentation in order to make reading/editing each other code seamlessly easy like reading our own code. There are four primary levels that are addressed: File Descriptions, Class Descriptions, Function/Method Descriptions, and Code Comments. 

### File Descriptions

For each code file created, you should include your name, preferred contact email, last date modified, and a brief description of code is contained in the file.

Example:

```python
'''
Copyright 2018, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 11/16/2018
Description: This module is the driver program for the Sparton AHRS.
'''
from sensorHub import SensorHubBase
import serial
import time
import struct
```

### Class Descriptions

When developing object-oriented base programs using classes, it is helpful to have a brief description of what objects of the class created will do. This docstring should be implemented directly before your class constructor.

Example:

```python
class SpartonAHRSDataPackets:
    '''
    This class implements the getters and setters commands for the Sparton AHRS.
    It handles the sending values to configure the device and request data specified
    data.
    '''

    def __init__(self, com_port):
        ...
```

###  Function Descriptions 

Probably the most important form of inline documentation are detailed functions description. A function description is composed of the 3 components: A description of what the function does, a list of what parameters are passed to the function, and a list what the function returns.  The input parameters and returns should be well described such as what the type is and if there are any default values.

Example:

```python
    def create_subscriber(self, topic, callback, timeout=.01, sub_port="5560"):
        '''
        Create a subscriber and connect it to mechoscore pub/sub handler to
        receiver data from a publisher using the same topic name.

        Parameters:
            topic: A well-defined topic name for subscriber to connect to
                    publisher of the same name.
            callback: A function to place the data received by the
                        subscriber. The first paramter of the callback
                        function is where the data will be passed.
            timeout: The time in seconds the poller will hold before
                    exiting if no messages are received. Keeps the direct
                    listening of messages from freezing up. Default .01 second
            sub_port: The port to connect the subscriber socket to mechoscore.
                        Default 5560
        Returns:
            N/A
        '''
```

### Commenting code

When writing code, you should take the time to make your code as readable as possible without needing comments, however there are still many cases where commenting is necessary. If you don't think a segment of code could be understood easily at first glance by another software member, give it a short comment describing what it does! Trust me , it will also make reading your own code easier in the long run!

Example:

```python
            #successful header byte
            if header_byte == self.success_header_byte:

                #Read second byte to confirm successful packet
                type_byte = ord(self.ahrs_serial.read())
                if type_byte == self.location_array[data_type][0]:

                    #read the given number of data bytes specified by location array
                    for idx in range(0, self.location_array[data_type][1] - 2):
                        ahrs_data_in.append(ord(self.ahrs_serial.read()))

                    #confirm correct termination of data packet
                    if ahrs_data_in[-1] != self.termination_byte:
                        return None

```

## How to Write WIKI Documentation

Beyond providing documentation within your code, writing reference documentation in a WIKI format provides future users easy navigation and reference to your software without actually having to dive into the meat of the code. For example, if you provide a lookup of all you functions, including descriptions of parameter inputs and outputs, future users can abstract the niddy griddy software as a "blockbox" and only worry about inputs and outputs. 

For this club, WIKI documentation will be posted on the github WIKI using the github markdown language. Each script you write should contain a WIKI reference guide that describes all of the primary functions implemented AND any theory behind algorithms that are used. 

### Example:

# Sparton AHRS Reference: Sparton AHRS Driver Program - AHRS.py
The Sparton GEDC-6 Attitude Heading Reference Systems(AHRS) provides heading, pitch, and roll data with reliable performance. It contains on-board "adaptive" algorithms to ensure accurate results from the 3-axis magnetometer, accelerometer, and gyroscope. This device communicates over simple 2-wire serial (UART).  

## Class SpartonAHRSDataPackets
This class implements the getters and setters commands for the Sparton AHRS. It handles the sending values to configure the device and request data specified.
​    data.
> **AHRS.SpartonAHRSDataPackets(com_port)**

Example Usage:
```python
sparton_ahrs = SpartonAHRSDataPackets('COM7')

while(1):
    sparton_ahrs.get_raw_magnetics() #request raw magnetic data
    
    #using serial, read the 9 byte data packet sent by the ahrs
```

> \_\_init\_\_(self, com_port)

```
Initializes connection with the AHRS device at a baud rate of 115200.
        Sets up the array of location values.

        Parameters:
            com_port: A string value of the serial COM port that the AHRS
                            device is connected to.
        Returns:
            N/A
```

> get_raw_magnetics(self)
```
Send request to get the raw magnetics from the magnetometers (Mx, My,
        and Mz). These are raw sensor readings and do not yet have any
        calibration. Note that this function is really only used for test purposes.
        NOT PRACTICAL FOR OFFICIAL USE.

        Reference: Software-Interface-Manual page 38

         Send: 3 Byte (0xA4,0x01,0xA0)

        Response: 9 Bytes (0xA4,0x01,<Mx>,<My>,<Mz as 16-bit integers MS
         byte first>,0xA0)

         Parameters:
            N/A
        Returns:
            raw_magnetics: 6-byte list of raw magnetics.      
```
> get_true_heading(self)
```
Send request to get the true heading. True heading is the magnetic
        heading.

        Reference: Software-Interface-Manual page 38.

        Send: 3 Bytes (0xA4, 0x02, 0xA0)

        Responds: 5 Bytes <0xA4, 0x02, <Heading as a 16-bit signed integer>,
                            0xA0)
        Heading (degrees) = 16-bit Heading value * (360/4096)
        Heading Range = 0.0 to + 359.9

        Returns:
            true_heading: The true heading in degrees from 0.0 to 359.9. If the
                            data could not be received, return an empty list.
```

> get_pitch_roll(self)
```
        Send request and receive data to get the pitch and roll of the platform.

        Reference: Sofware-Inference-Manual page 42.

        Send: 3 Bytes (0xA4, 0x06, 0xA0)

        Response: 7 Bytes (0xA4, 0x06, Pitch, Roll as 16-bit signed integers, 0xA0)

        Pitch(in degrees) = (Response) * 90/4096
        Pitch Range: -90 to +90

        Roll (in degrees) = (Response) * 180/4096
        Acceleration Vector Roll Range = -180 to 180

        Returns:
            pitch_roll: A list containing the pitch and roll
```

> _unpack(self, data_type)
```
        Read in the transmission from AHRS and extract all the bytes of the
        packet.

        Parameters:
            datatype: The type of data being read. Note: This should be one of
                    the keys in the locationArray(see constructor)
        Returns:
            ahrs_data_in: The raw data packet of the given data type. If there is
                        an error reading the data, return None. If there are no
                        datapacket to be read, return an empty list of data.
```



