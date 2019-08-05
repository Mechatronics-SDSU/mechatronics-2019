'''
Copyright 2019, Mohammad Shafi, All rights reserved
Author: Mohammad Shafi <ma.shafi99@gmail.com>
Last Modified: July 25th, 2019
Description: This script calculates poses of our detected objects we get from
the neural network using OpenCV's solvePnP function. It gives us translation and
rotation of these objects with respect to the camera
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
    def __init__(self):
        '''
        Initializes my distance calculator
        Params:
            N/A
        Returns:
            N/A
        '''
        self.detection = None
        self.x_coordinate = None
        self.second_x_coordinate = None
        self.y_coordinate = None
        self.second_y_coordinate =None
        self.width = None
        self.second_width = None
        self.height = None
        self.second_height = None
        self.difference = None
        self.threshold = None

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

    def set_coordinates(self, detect_list, detection, x, y, w, h):
        '''
        This function sets our three dimensional and two dimensional points depending on the detection.
        The three dimensional points are set using the acutal dimensions of the object. For example, the gate is 10
        feet wide, so the right side is set to (5,0) in real world space. Everything is calculated in terms of inches,
        then converted to feet. The two dimensional coordinates are set using Yolo's bounding boxes. Corners of objects
        in the real world are mapped to their respective corners when Yolo generates its bounding box for one of the objects
        Params:
            detect_list: List of all detections currently available
            detection: The detection in question that we are trying to solve for
            x: The center of the bounding box drawn by Yolo. Horizontal pixel coordinate
            y: THe center of the bounding box drawn by Yolo. Vertical pixel coordinate
            w: The width of the bounding box. In pixels
            h: The height of the bounding box. In pixels
        Returns:
            N/A
        '''
        #print(self.distortion_matrix)
        self.detection = detection
        self.x_coordinate = x
        self.y_coordinate = y
        self.width = w
        self.height = h

        label = self.detection[0]

        if(label == b'Dice'):
            self.min_coordinate = float(self.param_serv.get_param("Vision/Coordinates/dice/topleft"))
            self.center_coordinate = float(self.param_serv.get_param("Vision/Coordinates/dice/middle"))
            self.max_coordinate = float(self.param_serv.get_param("Vision/Coordinates/dice/bottomright"))

            self.three_dim_points = np.array([[self.min_coordinate, self.min_coordinate, self.center_coordinate],
                                              [self.center_coordinate, self.min_coordinate, self.center_coordinate],
                                              [self.max_coordinate, self.min_coordinate, self.center_coordinate],
                                              [self.min_coordinate, self.center_coordinate, self.center_coordinate],
                                              [self.center_coordinate, self.center_coordinate, self.center_coordinate],
                                              [self.max_coordinate, self.center_coordinate, self.center_coordinate],
                                              [self.min_coordinate, self.max_coordinate, self.center_coordinate],
                                              [self.center_coordinate, self.max_coordinate, self.center_coordinate],
                                              [self.max_coordinate, self.max_coordinate, self.center_coordinate]])

            self.two_dim_points = np.array([[(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate)],
                                            [(self.x_coordinate), (self.y_coordinate)],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate)],
                                            [(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate + (0.5 * self.height))],
                                            [(self.x_coordinate), (self.y_coordinate + (0.5 * self.height))],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate + (0.5 * self.height))]])

        elif(label == b'Buoy'):

            self.center_boordinate = float(self.param_serv.get_param("Vision/Coordinates/buoy/center"))
            self.left_boordinate = float(self.param_serv.get_param("Vision/Coordinates/buoy/left"))
            self.right_boordinate = float(self.param_serv.get_param("Vision/Coordinates/buoy/right"))
            self.top_boordinate = float(self.param_serv.get_param("Vision/Coordinates/buoy/top"))
            self.bottom_boordinate = float(self.param_serv.get_param("Vision/Coordinates/buoy/bottom"))

            self.three_dim_points = np.array([[self.left_boordinate, self.top_boordinate, self.center_boordinate],
                                              [self.center_boordinate, self.top_boordinate, self.center_boordinate],
                                              [self.right_boordinate, self.top_boordinate, self.center_boordinate],
                                              [self.left_boordinate, self.center_boordinate, self.center_boordinate],
                                              [self.center_boordinate, self.center_boordinate, self.center_boordinate],
                                              [self.right_boordinate, self.center_boordinate, self.center_boordinate],
                                              [self.left_boordinate, self.bottom_boordinate, self.center_boordinate],
                                              [self.center_boordinate, self.bottom_boordinate, self.center_boordinate],
                                              [self.right_boordinate, self.bottom_boordinate, self.center_boordinate]])

            self.two_dim_points = np.array([[(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate - (0.5 * self.height))],
                                            [(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate)],
                                            [(self.x_coordinate), (self.y_coordinate)],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate)],
                                            [(self.x_coordinate - (0.5 * self.width)), (self.y_coordinate + (0.5 * self.height))],
                                            [(self.x_coordinate), (self.y_coordinate + (0.5 * self.height))],
                                            [(self.x_coordinate + (0.5 * self.width)), (self.y_coordinate + (0.5 * self.height))]])

        elif(label == b'Gate Arm'):

            self.center = float(self.param_serv.get_param("Vision/Coordinates/gate/center")) #0.0
            self.max = float(self.param_serv.get_param("Vision/Coordinates/gate/max")) #5
            self.mid_max = float(self.param_serv.get_param("Vision/Coordinates/gate/mid")) #2.5
            self.quarter_max = float(self.param_serv.get_param("Vision/Coordinates/gate/quarter")) #1.25
            self.min = -1.0 * self.max #-5
            self.mid_min = -1.0 * self.mid_max #-2.5
            self.quarter_min = -1.0 * self.quarter_max #-1.25
            self.zero_pixel_error = float(self.param_serv.get_param("Vision/Coordinates/gate/pixel_error"))
            self.top_pixel_error = float(self.param_serv.get_param("Vision/Coordinates/gate/top_pixel_error"))
            self.arm_pixel_error = float(self.param_serv.get_param("Vision/Coordinates/gate/arm_pixel_error"))

            self.gate_shared_points = np.array([[self.center, self.center, self.center], #0, 0, 0
                                                [self.min, self.mid_min, self.center], #-5, -2.5, 0
                                                [self.max, self.mid_min, self.center]]) #5, -2.5, 0

            self.gate_top_points = np.array([ [self.mid_min, self.mid_min, self.center], #-2.5, -2.5, 0
                                              [self.center, self.mid_min, self.center], #0, -2.5, 0
                                              [self.mid_max, self.mid_min, self.center]]) #2.5, -2.5, 0

            self.gate_right_points = np.array([[self.max, self.quarter_min, self.center], #5, -1.25, 0
                                               [self.max, self.center, self.center], #5, 0, 0
                                               [self.max, self.quarter_max, self.center], #5, 1.25, 0
                                               [self.max, self.mid_max, self.center]]) #5, 2.5, 0

            self.gate_left_points = np.array([[self.min, self.quarter_min, self.center], #-5, -1.25, 0
                                              [self.min, self.center, self.center], #-5, 0, 0
                                              [self.min, self.quarter_max, self.center], #5, 1.25, 0
                                              [self.min, self.mid_max, self.center]]) #5, 2.5, 0

            for second_det in detect_list:
                self.second_x_coordinate, self.second_y_coordinate, self.second_width, self.second_height = second_det[2][0], second_det[2][1], second_det[2][2], second_det[2][3]
                self.difference = self.second_x_coordinate - self.x_coordinate

                if(second_det[0] == b'Gate Top'):
                    self.temp_three_dim_points = np.concatenate((self.gate_shared_points, self.gate_top_points), axis = 0)
                    if(self.difference < self.top_pixel_error and self.difference >= self.zero_pixel_error): #if pixel data is less than 10 percent of the image, data is bullshit
                        self.three_dim_points = np.concatenate((self.temp_three_dim_points, self.gate_left_points), axis = 0)
                    elif(self.difference > (-1.0 *(self.top_pixel_error)) and self.difference <= self.zero_pixel_error):
                        self.three_dim_points = np.concatenate((self.temp_three_dim_points, self.gate_right_points), axis = 0)

                    self.two_dim_points = np.array([[self.second_x_coordinate, self.y_coordinate],
                                                    [self.second_x_coordinate - (0.5 * self.second_width), self.second_y_coordinate],
                                                    [self.second_x_coordinate + (0.5 * self.second_width), self.second_y_coordinate],
                                                    [self.second_x_coordinate - (0.25 * self.second_width), self.second_y_coordinate],
                                                    [self.second_x_coordinate, self.second_y_coordinate],
                                                    [self.second_x_coordinate + (0.25 * self.second_width), self.second_y_coordinate],
                                                    [self.x_coordinate, self.y_coordinate - (0.25 * self.height)],
                                                    [self.x_coordinate, self.y_coordinate],
                                                    [self.x_coordinate, self.y_coordinate + (0.25 * self.hegiht)],
                                                    [self.x_coordinate, self.y_coordinate + (0.5) * self.height]])

                if(second_det[0] == b'Gate Arm'):
                    if(abs(self.difference) < self.arm_pixel_error): #if distance between the arms is less than a fifth of the image, data is bullshit
                        self.temp_three_dim_points = np.concatenate(self.gate_shared_points, self.gate_left_points)
                        self.three_dim_points = np.concatenate(self.temp_three_dim_points, self.gate_right_points)

                        if(self.difference <= self.zero_pixel_error and self.difference > self.arm_pixel_error): #right arm was detected first
                            self.two_dim_points = np.array([[self.x_coordinate - (self.difference * 0.5), self.y_coordinate],
                                                            [self.second_x_coordinate, self.second_y_coordinate - (0.5 * self.second_height)],
                                                            [self.x_coordinate, self.y_coordinate - (0.5 * self.height)],
                                                            [self.second_x_coordinate, self.second_y_coordinate - (0.25 * self.second_height)],
                                                            [self.second_x_coordinate, self.second_y_coordinate],
                                                            [self.second_x_coordinate, self.second_y_coordinate + (0.25 * self.second_height)],
                                                            [self.second_x_coordinate, self.second_y_coordinate + (0.5 * self.second_height)],
                                                            [self.x_coordinate, self.y_coordinate - (0.25 * self.height)],
                                                            [self.x_coordinate, self.y_coordinate],
                                                            [self.x_coordinate, self.y_coordinate + (0.25 * self.hegiht)],
                                                            [self.x_coordinate, self.y_coordinate + (0.5 * self.height)]])

                        if(self.difference >= self.zero_pixel_error  and self.difference < (-1 * self.arm_pixel_error)): #left arm was detected first
                            self.two_dim_points = np.array([[self.x_coordinate + (self.difference * 0.5), self.y_coordinate],
                                                            [self.x_coordinate, self.y_coordinate - (0.5 * self.height)],
                                                            [self.second_x_coordinate, self.second_y_coordinate - (0.5 * self.second_height)],
                                                            [self.x_coordinate, self.y_coordinate - (0.25 * self.height)],
                                                            [self.x_coordinate, self.y_coordinate],
                                                            [self.x_coordinate, self.y_coordinate + (0.25 * self.height)],
                                                            [self.x_coordinate, self.y_coordinate + (0.5 * self.hegiht)],
                                                            [self.second_x_coordinate, self.second_y_coordinate - (0.25 * self.second_height)],
                                                            [self.second_x_coordinate, self.second_y_coordinate],
                                                            [self.second_x_coordinate, self.second_y_coordinate + (0.25 * self.second_height)],
                                                            [self.second_x_coordinate, self.second_y_coordinate + (0.5 * self.second_height)]])



        else:
            pass

    def calculate_distance(self):
        '''
        This function takes the matrices set earlier, and then performs the necessary operations
        to successfully judge the pose of the object from the camera. The equation is as follows:
        image points = (Cammatrix dot(rt matrix))dot world points. The rt matrix is a 3 by 4 rt transform
        matrix that has a rotation component and a translation component. SolvePnP gives us these matrices
        as individual rotation and translation vectors
        Params:
            N/A
        Returns:
            rvec: Rotation vector to judge orientation of object with respect to camera
            tvec: Translation vector to judge distance of object with respect to camera
            z: z coordinate of the translation vector
        '''

        if (self.three_dim_points is None or self.two_dim_points is None):
            return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 0.0

        else:
            working, rvec, tvec = cv2.solvePnP(self.three_dim_points, self.two_dim_points, self.camera_matrix,self.distortion_matrix)
            inchvec = np.array([(float(tvec[0]/12.0)), float(tvec[1]/12.0), float(tvec[2]/12.0)])
            return rvec, inchvec, inchvec[2]
