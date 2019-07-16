'''
Copyright 2019, Mohammad Shafi, All rights reserved

Author: Mohammad Shafi <ma.shafi99@gmail.com>
'''
import os
import sys
import cv2
import numpy as np
from MechOS import mechos

PARAM_PATH = os.path.join("..", "Params")
sys.path.append(PARAM_PATH)
MECHOS_CONFIG_FILE_PATH = os.path.join(PARAM_PATH, "mechos_network_configs.txt")
from mechos_network_configs import MechOS_Network_Configs

class Distance_Calculator():
    '''
    This class initializes our required matrices using points from the parameter server,
    and detection data from yolo. It will then use openCV operations to interpret the data
    and give us accurate judgements on how far our objects are from the front of the sub.
    '''
    def __init__(self, detection, x, y, w, h):
        '''
        Initializes my distance calculator
        Params:
            detection: Detection object. Includes image with yolo's bouding box drawn around
            x: x coordinate of the bounding box
            y: y coordinate of the bounding box
            w: width of the bounding box
            h: height of the bounding box
        Returns:
            N/A
        '''
        self.detection = None
        self.x_coordinate = None
        self.y_coordinate = None
        self.width = None
        self.height = None

        configs = MechOS_Network_Configs(MECHOS_CONFIG_FILE_PATH)._get_network_parameters()

        self.param_serv = mechos.Parameter_Server_Client(configs["param_ip"], configs["param_port"])
        self.param_serv.use_parameter_database(configs["param_server_path"])

        self.focal_length_x = float(self.param_serv.get_param("Vision/solvePnP/camera_matrix/focal_length_x"))
        self.focal_length_y = float(self.param_serv.get_param("Vision/solvePnP/camera_matrix/focal_length_y"))
        self.optical_center_x = float(self.param_serv.get_param("Vision/solvePnP/camera_matrix/optical_center_x"))
        self.optical_center_y = float(self.param_serv.get_param("Vision/solvePnP/camera_matrix/optical_center_y"))

        self.camera_matrix = np.array([[self.focal_length_x, 0.0, self.optical_center_x],
                                      [0.0, self.focal_length_y, self.optical_center_y],
                                      [0.0, 0.0, 1.0]])

        self.distort_var_1 = float(self.param_serv.get_param("Vision/solvePnP/distortion_matrix/k1"))
        self.distort_var_2 = float(self.param_serv.get_param("Vision/solvePnP/distortion_matrix/k2"))
        self.distort_var_3 = float(self.param_serv.get_param("Vision/solvePnP/distortion_matrix/p1"))
        self.distort_var_4 = float(self.param_serv.get_param("Vision/solvePnP/distortion_matrix/p2"))
        self.distort_var_5 = float(self.param_serv.get_param("Vision/solvePnP/distortion_matrix/k3"))

        self.distortion_matrix = np.array([[self.distort_var_1, self.distort_var_2, self.distort_var_3, self.distort_var_4, self.distort_var_5]])

        self.two_dim_points = None
        self.three_dim_points = None

    def set_coordinates(self, detection_list, detection, x, y, w, h):
        '''
        This function sets our three dimensional and two dimensional points depending on the detection
        Params:
            N/A
        Returns:
            N/A
        '''
        #print(self.distortion_matrix)
        self.detection_list = detection_list
        self.detection = detection
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        label = self.detection[0]

        if(label == b'Dice'):
            self.min_coordinate = float(self.param_serv.get_param("Vision/Coordinates/dice/topleft"))
            self.center_coordinate = float(self.param_serv.get_param("Vision/Coordinates/dice/middle"))
            self.max_coordinate = float(self.param_serv.get_param("Vision/Coordinates/dice/bottomright"))
            self.three_dim_points = np.array([[self.min_coordinate, self.min_coordinate, self.min_coordinate],
                                              [self.center_coordinate, self.min_coordinate, self.min_coordinate],
                                              [self.max_coordinate, self.min_coordinate, self.min_coordinate],
                                              [self.min_coordinate, self.center_coordinate, self.min_coordinate],
                                              [self.center_coordinate, self.center_coordinate, self.min_coordinate],
                                              [self.max_coordinate, self.center_coordinate, self.min_coordinate],
                                              [self.min_coordinate, self.max_coordinate, self.min_coordinate],
                                              [self.center_coordinate, self.max_coordinate, self.min_coordinate],
                                              [self.max_coordinate, self.max_coordinate, self.min_coordinate]])

            self.two_dim_points = np.array([[(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate)],
                                            [(self.x_coordinate), (self.y_coordinate)],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate)],
                                            [(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate + (0.5 * self.height))],
                                            [(self.x_coordinate), (self.y_coordinate + (0.5 * self.height))],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate + (0.5 * self.height))]])

        else:
            pass

    def calculate_distance(self):
        '''
        This function takes the matrices set earlier, and then performs the necessary operations
        to successfully judge the pose of the object from the camera
        Params:
            N/A
        Returns:
            rvec: Rotation vector to judge orientation of object with respect to camera
            tvec: Translation vector to judge distance of object with respect to camera
            z: z coordinate of the translation vector
        '''

        if (self.three_dim_points is None or self.two_dim_points is None):
            return [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]

        else:
            working, rvec, tvec = cv2.solvePnP(self.three_dim_points,
                                               self.two_dim_points,
                                               self.camera_matrix,
                                               self.distortion_matrix)
            return rvec, tvec, tvec[2]
