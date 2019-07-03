import sys
import os

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

from MechOS import mechos
import time
import imagezmq
import cv2
import threading


class Vision(threading.Thread):
    '''
    The class contains the main components (functions and attributes)
    for the vision system on the sub.
    '''
    def __init__(self):
        '''
        Initialize the vision system by retrieving the necessary
        parameters.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        super(Vision, self).__init__()

        #Get the mechos network parameters
        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()


        #---IMAGEZMQ BASED COMMUNICATION---#
        image_zmq_connection = "%s:%s" %("tcp://192.168.1.1", configs["video_port"])
        self.image_publisher = imagezmq.ImageSender(connect_to=image_zmq_connection)

        self.test_image = cv2.imread("test_image.png")
        #----------------------------------#

        #Opencv video capture object
        self.video_capture = cv2.VideoCapture(1)

        #Resizing the video
        #TODO: Make this a parameter in the parameter server.
        width = 600
        height = 800
        width_set = self.video_capture.set(3, width) #Sets width
        if( not width_set):
            print("[ERROR]: Failed to set the video capture width to %s!" % width)

        height_set = self.video_capture.set(4, height) #Sets height
        if not height_set:
            print("[ERROR]: Failed to set the video capture height to %s!" % height)

        self.run_thread = True
        self.daemon = True
        sys.exitfunc = self.kill

    def run(self):
        '''
        The run loop for performing the vision operations and sending
        the video video stream.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        video_stream_test = False
        while(self.run_thread):

            #Attempt
            if(video_stream_test):
                self.image_publisher.send_image("test", self.test_image)
            else:
                successful_capture, video_frame = self.video_capture.read()

                self.image_publisher.send_image("Vid", video_frame)


    def kill(self):
        '''
        Safe clean up when killing this thread.

        Paramaeters:
            N/A
        Returns:
            N/A
        '''
        print("[INFO]: Killing vision thread. Releasing Resources.")
        self.video_capture.release()

if __name__ == "__main__":
    vision = Vision()
    vision.run()
