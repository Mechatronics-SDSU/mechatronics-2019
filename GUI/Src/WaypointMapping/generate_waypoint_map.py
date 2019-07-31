'''
'''
import cv2
import numpy as np
import math

class Generate_Waypoint_Map:

    def __init__(self, map_image,pixel_distance_ratio, north_angle):
        '''
        Initialize the waypoint map generator.

        Parameters:
            map_image: The location to the google maps image.
            pixel_distance_ratio: Number of pixels per foot.
            north_angle: The angle with respect to a verticle axis up where north faces (0-360)
        '''
        #Keep an original map image in case you delete a waypoint
        self.original_map_image = cv2.imread(map_image)
        self.temporary_map_image = self.original_map_image.copy() #This is where stuff will be drawn intermediately
        self.waypointed_map_image = self.original_map_image.copy() #The map image with the drawn waypoints

        self.pixel_distance_ratio = pixel_distance_ratio
        self.north_angle = north_angle

        self.drawing = False

        cv2.namedWindow('Map_Image')
        cv2.setMouseCallback("Map_Image", self.collect_waypoint_callback)

        #The pixel that is considered the origin
        self.origin_pixel = [719.0, 443.0]

        #The waypoint list relative to the origin. This is the North/East posisition
        self.waypoint_list = []

    def calculate_position(self, x_coordinate, y_coordinate):
        '''
        '''
        north_angle_radians = math.radians(self.north_angle)
        north_position = ((self.origin_pixel[0] - y_coordinate)*math.cos(north_angle_radians) + \
                         (x_coordinate - self.origin_pixel[1])*-1*math.sin(north_angle_radians)) / self.pixel_distance_ratio

        east_position = ((self.origin_pixel[0] - y_coordinate)*math.sin(north_angle_radians) + \
                         (x_coordinate - self.origin_pixel[1])*math.cos(north_angle_radians)) / self.pixel_distance_ratio

        self.waypoint_list.append([north_position, east_position])
        print(north_position, east_position)

    def collect_waypoint_callback(self, event, x_coordinate, y_coordinate, flags, param):
        '''
        This is the function called on a mouse click event on the map image. It
        will draw the waypoint on the map and record the waypoints.

        Parameters:
            event:
            x_coordinate: The x pixel coordinate of the mouse press.
            y_coordinate: The y pixel coordinate of the mouse press.
            flags - params: Not used, but needed by opencv (see opencv docs)
        '''
        self.waypointed_map_image = self.temporary_map_image.copy()
        if(event == cv2.EVENT_LBUTTONDOWN):
            self.drawing = True
            self.x_coordinate = x_coordinate
            self.y_coordinate = y_coordinate
            print(x_coordinate)
            cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, (255, 0, 255), -1)

        elif event == cv2.EVENT_MOUSEMOVE:
            if(self.drawing == True):
                cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, (255, 0, 255), -1)

        elif event == cv2.EVENT_LBUTTONUP:

            if(self.drawing == True):
                self.drawing = False
                cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, (255, 0, 255), -1)
                self.temporary_map_image = self.waypointed_map_image.copy()
                print(x_coordinate, y_coordinate)
                self.calculate_position(x_coordinate, y_coordinate)
    
    def run(self):
        '''
        '''
        while(1):
            cv2.imshow("Map_Image", self.waypointed_map_image)
            k = cv2.waitKey(1) & 0xFF

            if(k == 27):
                break

if __name__ == "__main__":
    map_image = "transdec_pool_a.png"
    pixel_distance_ratio = 8.1
    north_angle = 0
    generate_waypoint_map = Generate_Waypoint_Map(map_image, pixel_distance_ratio, north_angle)
    generate_waypoint_map.run()
