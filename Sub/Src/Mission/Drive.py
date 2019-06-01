import sys
import os
PROTO_PATH = os.path.join("..", "..", "..", "Proto")
sys.path.append(os.path.join(PROTO_PATH, "Src"))
sys.path.append(PROTO_PATH)
import desired_position_pb2

HELPER_PATH = os.path.join("..", "Helpers")
sys.path.append(HELPER_PATH)
import util_timer

import time
import math
import threading

class Drive:
    '''
    This class is the task that executes simply driving to a specified
    position.
    '''

    def __init__(self, mission_commander_object, desired_pos, wait_time, buffer_zone, task_name="simple_drive",
                timeout=2, pos_reference="relative"):
        '''
        Initialize the Simple Drive task with the parameters to get the sub
        to drive to a desired position relative to its current position.

        Parameters:
            mission_commander_object: The mission_commander_object should be the object that calls this class. It controls
                                    all the tasks of the missions and contains the MechOS node to send desired positions and 
                                    receive current position positions. Hence it will be used to get the data for the current position
                                    thread and send data with the desired position publisher. Must be of type mission commander.
            current_pos_subscriber: The MechOS subscriber object to recieve current position/navigation data from the sensor_driver.
                                    It shoud have topic name "NAV" and receive messages with the "navigation_data" protobuff.
            desired_pos: The desired position of the sub as a list of floats
                                [roll, pitch, yaw, x_pos, y_pos, z_pos(depth)]
            wait_time: The time in seconds the sub should wait at the desired position
                        before ending the task.
            pos_reference: Move the sub in the x and y position either "relative" to the current
                            position or "absolute" to the origin position.
            buffer_zone: The allowable radius around the desired_position (in ft) that the sub
                        consideres successful to completeing the mission to making it to the position
                        desired.
            time_out: The amount of time in MINUTES that the sub has to attempt to complete the mission.
        '''
        #Load the passed in parameters
        self.mission_commander_object = mission_commander_object
        self.desired_pos = desired_pos
        self.wait_time = wait_time * 60 #put in seconds
        self.pos_reference = pos_reference
        self.buffer_zone = buffer_zone
        self.task_name = task_name
        self.timeout = timeout * 60 #put in seconds
        self.task_complete = False

        #Initialize timer
        self.timeout_timer = util_timer.Timer()
        self.timer_thread = threading.Thread(target=self.timer_thread_callback)
        self.timer_thread.daemon = True
        self.task_timed_out = False
        
        #Initialize Position proto
        self.desired_pos_proto = desired_position_pb2.DESIRED_POS()
        
        #Print initialization status
        print("Task", self.task_name, "of type Drive is initialized")
    
    def print_task_information(self):
        '''
        Print the information about the given task

        Parameters:
            N/A
        Returns:
            N/A
        '''
        print()
        print("Task Type: Drive")
        print("Task Name:", self.task_name)
        print("Position Reference:", self.pos_reference)
        print("Desired Position: roll=%.2fdeg, pitch=%.2fdeg, yaw=%.2fdeg, x=%.2fft, y=%.2fft, z(depth)=%.2fft" % (self.desired_pos[0], 
                                                                                                    self.desired_pos[1], 
                                                                                                    self.desired_pos[2],
                                                                                                    self.desired_pos[3],
                                                                                                    self.desired_pos[4],
                                                                                                    self.desired_pos[5]))
        print("Timeout: %.2fs" % self.timeout)
        print("Buffer Zone: %.2fft" % self.buffer_zone)
        print("Wait Time(Hold Final Position Time): %.2fs" % self.wait_time)

    def timer_thread_callback(self):
        '''
        Callback function that monitors the current time of the task.

        Parameters:
            N/A
        Returns:
            self.task_timed_out: Boolean for if the task has timed out or not.
        '''

        #Start timeout timer
        self.timeout_timer.restart_timer()
        self.elapsed_time = 0
        while (not self.task_complete) and (not self.task_timed_out):
            self.elapsed_time = self.timeout_timer.net_timer()
            if(self.elapsed_time > self.timeout):
                self.task_complete = False
                self.task_timed_out = True
        return self.task_timed_out

    def set_desired_position_proto(self, roll, pitch, yaw, x_pos, y_pos, depth, zero_pos, pos_ref):
        '''
        Configure the desired_position_proto. Return the serialize proto

        Parameters:
            roll: The desired roll of the angle of the sub
            pitch: The desired pitch angle of the sub
            yaw: The deisred yaw angle(heading) of the sub
            x_pos: The desired x posititon of the sub. If pos_ref is "absolute" then this will be the abolute x value to go to.
                    elif pos_ref is "relative", then this will be the translation distance in the x direction
            y_pos: The desired y posititon of the sub. If pos_ref is false then this will be the abolute y value to go to.
                    elif pos_ref is true, then this will be the translation distance in the y direction
            depth: The desired depth in ft.
            zero_pos: Set the current x and y position as origin.
            pos_ref: If "absolute" then the sub x and y are absolute coordinate positions relative to the set origin. Else
                        if "relative" then x and y are the distances to translate. 

        Returns:
            serialized_pos_proto: The protobuf serialized and ready to publish.
        '''
        self.desired_pos_proto.roll = roll
        self.desired_pos_proto.pitch = pitch
        self.desired_pos_proto.yaw = yaw
        self.desired_pos_proto.depth = depth
        self.desired_pos_proto.x_pos = x_pos
        self.desired_pos_proto.y_pos = y_pos
        self.desired_pos_proto.zero_pos = zero_pos
        self.desired_pos_proto.pos_ref = pos_ref

        serialized_pos_proto = self.dest_pos_proto.SerializeToString()

    def orient_yaw_towared_dest_pos(self):
        '''
        Orient the subs yaw to face the desired position. Also set the depth if necessary. Hold current x and y position.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        #Calculate the Yaw angle needed to face desired position
        #Get the current position
        error_x = math.radians(self.desired_pos[3] - current_pos[3])
        error_y = math.radians(self.desired_pos[4] - current_pos[4])
        pointing_yaw = math.degrees(math.atan2(error_y / error_x)) #atan2 considers the sign of x and y
        self.desired_pos_proto.yaw = pointing_yaw #set the yaw to face the desired position

        serialized_dest_proto = self.set_desired_position_proto(roll=0, pitch=0, yaw=pointing_yaw, depth=self.desired_pos[5], 
                                                                x_pos=current_pos[3], y_pos=current_pos[4], zero_pos=False, pos_ref=False)
        
        #Publish the desired position proto to move yaw and depth
        self.mission_commander_object.desired_pos_publisher.publish(serialize_dest_proto)
        
        while((abs(pointing_yaw - current_pos[3]) > self.yaw_tolerance) 
                        and (abs(self.desired_pos[5] - current_pos[5]) > self.depth_tolerance)):
            #Get current position of the sub           
            current_pos = self.mission_commander_object.current_pos
            
            #If mission timed out
            if(self.task_timed_out):
                self.task_complete = False
                print("Task", self.task_name, "timed out.")
                return False

        print("Task", self.task_name, "successfully oriented yaw to face desired_position.")
        return True    

    def run(self):
        '''
        Run and execute the Drive task. The drive task is completed successfully if 
        the sub gets in the buffer zone of the desired area and waits it correct amount of wait time.
        If the timeout is met before the sub completely finishes the mission, the mission will be considered
        a fail, and the sub will move onto the next mission.

        Parameters:
            N/A

        Returns:
            self.task_complete: A boolean of true or false to signfiy if the mission was completed successfully.
        '''
        print("Starting task...")
        self.print_task_information()

        #Start timeout timer thread
        self.timer_thread.start()

        #If absolute movement
        if(self.pos_reference == "absolute"):
            
            #Make the sub face it's yaw towards the desired_position
            sub_oriented = self.orient_yaw_towared_dest_pos()

            if(not sub_oriented): #If sub orientation fails
                return False #Exit the task because of timeout
            
            #Now with the sub at the desired depth and facing the desired position, drive towards
            #the desired position.
            current_pos = self.mission_commander_object.current_pos
            serialized_dest_proto = self.set_desired_position_proto(roll=0, pitch=0, yaw=current_pos[2], depth=self.desired_pos[5], 
                                                                x_pos=self.desired_pos[3], y_pos=self.desired_pos[4], zero_pos=False, 
                                                                pos_ref=False)
        #If position reference for movement is relative
        elif(self.pos_reference == "relative"):
            serialized_dest_proto = self.set_desired_position_proto(roll=0, pitch=0, yaw=current_pos[2], depth=self.desired_pos[5], 
                                                                x_pos=self.desired_pos[3], y_pos=self.desired_pos[4], zero_pos=False, 
                                                                pos_ref=True)
        if(self.task_timed_out):
            self.task_complete = False
            print("Task", self.task_name, "timed out.")
            return False
            
        #Publish desired position to movement controller
        self.mission_commander_object.desired_pos_publihser.publish(serialized_dest_proto)

        #Once the sub is in the buffer zone of the desired position, then wait for the wait time.
        in_buffer_zone =False
        while not in_buffer_zone:
                
            #check if task has timedout
            if(self.task_timed_out):
                self.task_complete = False
                print("Task", self.task_name, "timed out.")
                return False

            #Check if the sub is in the bufferzone of the desired_position
            current_pos = self.mission_commander_object.current_pos
            dist_from_desired_pos = sqrt( (current_pos[3] - self.desired_pos[3])**2 + (current_pos[4] - self.desired_pos[4])**2 )
            if(dist_from_desired_pos <= self.buffer_zone):
                in_buffer_zone = True
                print("Task", self.task_name, "is within the buffer zone of the desired position.")
                break
                
        #Since the sub is in the buffer zone, wait at the given position for the wait time before exiting
        #the current task
        wait_timer = util_timer.Timer()
        wait_timer.restart_timer()
        waited_time = 0
        while(waited_time <= self.wait_time):

            if(self.task_timed_out):
                self.task_complete = False
                print("Task", self.task_name, "timed out.")
                return False
            wait_time = self.wait_timer.net_timer()
            
        #Task completed successfully
        print("Task", self.task_name, "completed successfully! Total time:", self.elapsed_time)
        self.task_complete = True
        return self.task_complete

        
    
                
            

