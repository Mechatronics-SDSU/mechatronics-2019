'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved
Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 07/1/2019
Description: This module contains functions to perform basic movements of the
            sub that can be utilized in missitons.
'''
import sys
import os
import time
import math
HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

MESSAGE_TYPE_PATH = os.path.join("..", "..", "Message_Types")
sys.path.append(MESSAGE_TYPE_PATH)
from desired_poisition_message import Desired_Position_Message

from MechOS import mechos
from MechOS.simple_messages.float_array import Float_Array


class Drive_Functions:
    '''
    A class containing basic functions for movements of the sub.
    Helpful for constructing missions.
    '''
    def __init__(self, mission_commander_obj):
        '''
        Parameters:
            N/A
        Returns:
            N/A
        '''

        self.timeout_timer = util_timer.Timer()

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        #Create mechos node
        self.drive_functions_node = mechos.Node("DRIVE_FUNCTIONS", '192.168.1.14', '192.168.1.14')
        self.desired_position_publisher = self.drive_functions_node.create_publisher("DESIRED_POSITION", Desired_Position_Message(), protocol="tcp")
        self.nav_data_subscriber = self.driver_functions_node.create_subscriber("SENSOR_DATA", Float_Array(6), self.__update_sensor_data, protocol="udp", queue_size=1)

        #Start a thread to listen for sensor data.
        self.sensor_data_thread = threading.Thread(target=self._update_sensor_data_thread, daemon=True)
        self.sensor_data_thread.start()

        #A boolean to specifiy if the drive functions are availible to run
        #This is used in case missions are canceled and does not want these functions to be able to use.
        self.drive_functions_enabled = True

    def _update_sensor_data_thread(self):
        '''
        Update the sensor data that this drive functions node subscribes to.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        while(1):
            self.drive_functions_node.spin_once()
            time.sleep(0.001)

    def __update_sensor_data(self,sensor_data):
        '''
        Update the sensor data

        Parameters:
            sensor_data: The sensor data from sensor_driver.
        Returns:
            n/a
        '''
        self.sensor_data = sensor_data

    def send_desired_position(self, desired_position):
        '''
        Publish the desired position of the sub using the desired position publisher.

        Parameters:
            desired_parameters: The desired position [roll, pitch, yaw, North Pos., East Pos.]

        Returns:
            N/A
        '''
        print("[INFO]: Sending Position\n", desired_position)
        self.desired_position_publisher.publish(desired_position)

    def get_yaw_error(self,current_yaw, desired_yaw):
        '''
        Function calculates the error in yaw between the current_yaw and desired
        yaw.

        Parameters:
            current_yaw: The current_yaw of the sub
            desired_yaw: The desired_yaw of the sub
        Returns:
            yaw_error: The error in degrees between the current and desired yaw
        '''
        yaw_error = desired_yaw - current_yaw
        if(abs(yaw_error) > 180):

            if(yaw_error < 0):
                yaw_error = yaw_error + 360
            else:
                yaw_error = yaw_error - 360
        return(yaw_error)

    def get_distance_to_position(self, current_north_position, current_east_position, desired_north_position, desired_east_position):
        '''
        Get the linear distance between the current position and desired position

        Parameters:
            current_north_position:
            current_east_position
            desired_north_position
            desired_east_position
        Returns:
            distance: The distance in ft to the desired position
        '''
        north_error = desired_north_position - current_north_position
        east_error = desired_east_position - current_east_position

        distance = math.sqrt( (north_error**2) + (east_error**2))

        return(distance)

    def move_to_depth(self, desired_depth, buffer_zone=0.0, timeout=None, desired_orientation={}):
        '''
        Go to the desired depth. This function will exit with success if
        the sub reaches within the buffer zone of the desired_depth. Note
        that the sub will still try to hold the depth after exiting this function.
        This is simply to abstract the move.

        Parameters:
            desired_depth: The desired_depth in feet that the sub
            should reach.
            buffer_zone: The buffer zone bubble in feet that can be considered
                        successfully making the depth dive.
            timeout: The amount of time this function can loop before exiting.
                    If it doesn't reach the buffer_zone in time, the function
                    will exit.
            desired_orientation: If None, use the current North, East, and
                                and yaw values to do the depth dive. Else use the
                                desired_orientation dictionary where you can set
                                between 1 and all the follow orientations.
                                {"yaw":<val>, "north_pos":<val>, "east_pos":<val>}
        '''

        current_position = self.sensor_data

        desired_position = [0.0, 0.0] + current_position[2:5] + [desired_depth]

        #If any of these keys are in desired_orientation, then hold that position while yawing
        orientation_keys = {"yaw":2, "north_pos":3, "east_pos":4}

        for orientation_to_lock in desired_orientation:
            index = orientation_keys[orientation_to_lock]
            desired_position[index] = desired_orientation[orientation_to_lock]

        self.send_desired_position(desired_position)

        #Begin the timeout timer.
        self.timeout_timer.restart_timer()

        while(abs(desired_depth - current_position[5]) > buffer_zone):

            if not self.drive_functions_enabled:
                print("[WARNING]: Cannot Execute drive function because the drive functions are disabled.")
                return False, desired_depth

            if(timeout != None):
                if(self.timeout_timer.net_timer() > timeout):
                    print("[WARNING]: Move to depth timed out. Depth error", current_position[5] - desired_depth)
                    current_position = self.sensor_data
                    return False, desired_depth

            current_position = self.sensor_data

        print("[INFO]: Move to depth succeeded to getting to depth:", desired_depth)
        return True, desired_depth


    def move_to_face_position(self, north_position, east_position, buffer_zone=0.0, timeout=None, desired_orientation={}):
        '''
        Re-orient the yaw position to face the north / east coordinate (relative to
        the set zero or origin position).

        Parameters:
            north_position: The north position component of the position yaw
                        should face.
            east_positon: The east position component ofof the position yaw should
                        face
            buffer_zone: The buffer zone in degrees at which the sub is considered
                    to have sucessfully reached the correct yaw. Default = 0
            timeout: The amount of time this function can loop before exiting. If
                        it doesn't rech the buffer_zone in time, the function
                        will exit
            desired_orientation: If None, hold the current North, East, and Depth
                                will orienting to face position.
        '''

        current_position = self.sensor_data
        desired_position = [0.0, 0.0, 0.0] + current_position[3:]

        #If any of these keys are in desired_orientation, then hold that position while yawing
        orientation_keys = {"north_pos":3, "east_pos":4, "depth":5}

        for orientation_to_lock in desired_orientation:
            index = orientation_keys[orientation_to_lock]
            desired_position[index] = desired_orientation[orientation_to_lock]

        north_dist = north_position - current_position[3]
        east_dist = east_position - current_position[4]

        desired_yaw = math.degrees(math.atan2(east_dist, north_dist))
        if(desired_yaw < 0):
            desired_yaw = 360 + desired_yaw

        desired_position[2] = desired_yaw

        self.send_desired_position(desired_position)

        #Begin the timeout timer.
        self.timeout_timer.restart_timer()

        yaw_error = self.get_yaw_error(current_position[2], desired_yaw)

        while(abs(yaw_error) > buffer_zone):

            if not self.drive_functions_enabled:
                print("[WARNING]: Cannot Execute drive function because the drive functions are disabled.")
                return False, desired_depth

            if(timeout != None):
                if(self.timeout_timer.net_timer() > timeout):
                    print("[WARNING]: Move to face position timed out. Yaw Error:", yaw_error)
                    current_position = self.sensor_data
                    return False, desired_yaw

            current_position = self.sensor_data
            yaw_error = self.get_yaw_error(current_position[2], desired_yaw)

        print("[INFO]: Move to face position succeeded. Facing coordinate: (%0.2fft, %0.2fft)" % (north_position, east_position))
        return True, desired_yaw

    def move_to_yaw(self, desired_yaw, buffer_zone=0.0, timeout=None, desired_orientation={}):
        '''
        Re-orient the yaw position to face the the new desired yaw.

        Parameters:
            yaw_position: The desired yaw position in degrees (range [0, 360])
            buffer_zone: The buffer zone in degrees at which the sub is considered
                    to have sucessfully reached the correct yaw. Default = 0
            timeout: The amount of time this function can loop before exiting. If
                        it doesn't rech the buffer_zone in time, the function
                        will exit
            desired_orientation: If None, hold the current North, East, and Depth
                                will orienting to face position.
        '''

        current_position = self.sensor_data
        desired_position = [0.0, 0.0, desired_yaw] + current_position[3:]

        #If any of these keys are in desired_orientation, then hold that position while yawing
        orientation_keys = {"north_pos":3, "east_pos":4, "depth":5}

        for orientation_to_lock in desired_orientation:
            index = orientation_keys[orientation_to_lock]
            desired_position[index] = desired_orientation[orientation_to_lock]

        self.send_desired_position(desired_position)

        #Begin the timeout timer.
        self.timeout_timer.restart_timer()

        yaw_error = self.get_yaw_error(current_position[2], desired_yaw)

        while(abs(yaw_error) > buffer_zone):

            if not self.drive_functions_enabled:
                print("[WARNING]: Cannot Execute drive function because the drive functions are disabled.")
                return False, desired_depth

            if(timeout != None):
                if(self.timeout_timer.net_timer() > timeout):
                    print("[WARNING]: Move to face position timed out. Yaw Error:", yaw_error)
                    current_position = self.sensor_data
                    return False, desired_yaw

            current_position = self.sensor_data
            yaw_error = self.get_yaw_error(current_position[2], desired_yaw)

        return True, desired_yaw

    def move_to_position_hold_orientation(self, north_position, east_position, buffer_zone=0.0, timeout=None, desired_orientation={}):
        '''
        Re-orient the yaw position to face the north / east coordinate (relative to
        the set zero or origin position).

        Parameters:
            north_position: The north position to drive to
            east_positon: The east position to drive to.
            buffer_zone: The buffer zone in degrees at which the sub is considered
                    to have sucessfully reached the correct position.
            timeout: The amount of time this function can loop before exiting. If
                        it doesn't rech the buffer_zone in time, the function
                        will exit.
            desired_orientation: If None, then use the current yaw and depth while
                                moving to the desired_position. Else pass a Dictionary
                                with 1 or all of the following keys with their desired
                                values.
                                {"depth":<val>, "yaw":<val>}
        '''
        #Get the current position
        current_position = self.sensor_data

        desired_position = [0.0, 0.0] + [current_position[2]] + [north_position, east_position] + [current_position[5]]

        #If any of these keys are in desired_orientation, then hold that position while yawing
        orientation_keys = {"yaw":2, "depth":5}

        for orientation_to_lock in desired_orientation:
            index = orientation_keys[orientation_to_lock]
            desired_position[index] = desired_orientation[orientation_to_lock]

        self.send_desired_position(desired_position)

        #Begin the timeout timer.
        self.timeout_timer.restart_timer()

        distance_to_position = self.get_distance_to_position(current_position[3], current_position[4], north_position, east_position)

        while(abs(distance_to_position) > buffer_zone):

            if not self.drive_functions_enabled:
                print("[WARNING]: Cannot Execute drive function because the drive functions are disabled.")
                return False, desired_depth

            if(timeout != None):
                if(self.timeout_timer.net_timer() > timeout):
                    print("[WARNING]: Move to position while holding orientatio timed out. Distance to position:", distance_to_position)
                    current_position = self.sensor_data
                    return False, north_position, east_position
            distance_to_position = self.get_distance_to_position(current_position[3], current_position[4], north_position, east_position)
            current_position = self.sensor_data

        print("[INFO]: Move to position while holding orientation succeeded. At position (%0.2fft, %0.2fft)" % (north_position, east_position))
        return True, north_position, east_position

    def move_x_direction(self, distance_x, buffer_zone, timeout=None, desired_orientation={}):
        '''
        Move in the x direction (forward/backward) distance_x amount of feet.

        Parameters:
            distance_x: The distance in feet to move in the x direction. If positive,
                        the sub will move forward. Else if negative, the sub will move
                        backwards.
            buffer_zone: The tolerance that x direction move can have.
            timeout: The amount of time this function can loop before exiting. If
                        it doesn't rech the buffer_zone in time, the function
                        will exit
        '''

        current_position = self.sensor_data

        #If any of these keys are in desired_orientation, then hold that position while yawing

        #Calculate what the desired north and east positions are to make that
        #corresponds to how far to move forward.
        if("yaw" in desired_orientation.keys()):
            current_yaw = math.radians(desired_orientation["yaw"])
        else:
            current_yaw = math.radians(current_position[2])
        north_position = distance_x * math.cos(current_yaw) + current_position[3]
        east_position = distance_x * math.sin(current_yaw) + current_position[4]

        return(self.move_to_position_hold_orientation(north_position, east_position, buffer_zone, timeout, desired_orientation))

    def move_y_direction(self, distance_y, buffer_zone, timeout=None, desired_orientation={}):
        '''
        Move in the y direction (right/left) distance_y amount of feet.

        Parameters:
            distance_y: The distance in feet to move in the y direction. If positive,
                        the sub will move right. Else if negative, the sub will move
                        left.
            buffer_zone: The tolerance that y direction move can have.
            timeout: The amount of time this function can loop before exiting. If
                        it doesn't rech the buffer_zone in time, the function
                        will exit
        '''

        current_position = self.sensor_data

        #Calculate what the desired north and east positions are to make that
        #corresponds to how far to move forward.
        current_yaw = math.radians(current_position[2])
        north_position = (-1 * distance_y * math.sin(current_yaw)) + current_position[3]
        east_position = (distance_y * math.cos(current_yaw))  + current_position[4]

        return(self.move_to_position_hold_orientation(north_position, east_position, buffer_zone, timeout, desired_orientation))
