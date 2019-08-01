'''
'''
import cv2
import numpy as np
import math
import json
import csv

class Generate_Waypoint_Map:

    def __init__(self, map_image, map_json, waypoint_save_file):
        '''
        Initialize the waypoint map generator.

        Parameters:
            map_image: The location to the google maps image.
            map_json: The json file containing the pixel_distance ratio and
                        the north angle.
        '''
        #Keep an original map image in case you delete a waypoint
        self.original_map_image = cv2.imread(map_image)
        self.temporary_map_image = self.original_map_image.copy() #This is where stuff will be drawn intermediately
        self.waypointed_map_image = self.original_map_image.copy() #The map image with the drawn waypoints

        with open(map_json, 'r') as read_map_json:
            map_data = json.load(read_map_json)

        self.pixel_distance_ratio = map_data["pixel_distance_ratio"]
        self.north_angle = map_data["north_angle"]

        #State of drawing the points on the image.
        self.drawing = False

        cv2.namedWindow('Map_Image')
        cv2.setMouseCallback("Map_Image", self.collect_waypoint_callback)

        #The pixel that is considered the origin
        self.origin_pixel = [0.0, 0.0]

        #The waypoint list relative to the origin. This is the North/East posisition
        self.waypoint_list = []
        self.waypoint_save_file = waypoint_save_file

        self.origin_color = (0, 255, 0)
        self.waypoint_color = (255, 0, 255)

        self.setting_origin = True

    def set_map(self, map_image, map_json):
        '''
        Reload a new map given the location to the map image

        Parameters:
            map_image: The location of the google maps image
        Returns:
            N/A
        '''
        #Keep an original map image in case you delete a waypoint
        self.original_map_image = cv2.imread(map_image)
        self.temporary_map_image = self.original_map_image.copy() #This is where stuff will be drawn intermediately
        self.waypointed_map_image = self.original_map_image.copy() #The map image with the drawn waypoints

        with open(map_json, 'r') as read_map_json:
            map_data = json.load(read_map_json)

        self.pixel_distance_ratio = map_data["pixel_distance_ratio"]
        self.north_angle = map_data["north_angle"]

        #State of drawing the points on the image.
        self.drawing = False

        #The pixel that is considered the origin
        self.origin_pixel = [0.0, 0.0]

        #The waypoint list relative to the origin. This is the North/East posisition
        self.waypoint_list = []

        self.setting_origin = True

    def calculate_position(self, x_coordinate, y_coordinate):
        '''
        '''
        north_angle_radians = math.radians(self.north_angle)
        north_position = ((self.origin_pixel[0] - y_coordinate)*math.cos(north_angle_radians) + \
                         (x_coordinate - self.origin_pixel[1])*-1*math.sin(north_angle_radians)) / self.pixel_distance_ratio

        east_position = ((self.origin_pixel[0] - y_coordinate)*math.sin(north_angle_radians) + \
                         (x_coordinate - self.origin_pixel[1])*math.cos(north_angle_radians)) / self.pixel_distance_ratio

        self.waypoint_list.append([x_coordinate, y_coordinate, north_position, east_position])
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

        if(self.setting_origin):
            color = self.origin_color
        else:
            color = self.waypoint_color

        if(event == cv2.EVENT_LBUTTONDOWN):
            self.drawing = True
            self.x_coordinate = x_coordinate
            self.y_coordinate = y_coordinate


            cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, color, -1)

        elif event == cv2.EVENT_MOUSEMOVE:
            if(self.drawing == True):
                cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, color, -1)

        elif event == cv2.EVENT_LBUTTONUP:

            if(self.drawing == True):

                if(self.setting_origin):
                    self.origin_pixel = [y_coordinate, x_coordinate]
                    self.setting_origin = False
                self.drawing = False
                cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, color, -1)
                print(x_coordinate, y_coordinate)
                #Draw line between points
                if(len(self.waypoint_list) > 0):
                    prev_coordinates = tuple((self.waypoint_list[-1])[0:2])
                    cv2.line(self.waypointed_map_image, prev_coordinates, (x_coordinate, y_coordinate), (0, 0, 255), 1)

                self.temporary_map_image = self.waypointed_map_image.copy()

                self.calculate_position(x_coordinate, y_coordinate)

    def run(self):
        '''
        '''
        while(1):
            cv2.imshow("Map_Image", self.waypointed_map_image)
            k = cv2.waitKey(1) & 0xFF

            if(k == 27):
                break
            if(k == ord('o')):
                print("Setting Origin Picked")
                self.setting_origin = True

            if(k == ord('s')): #Save the points to a waypoint file
                print("Saving Waypoints")

                if(len(self.waypoint_list) > 1):

                    with open(self.waypoint_save_file, 'w') as write_waypoints_file:
                        waypoints_csv_writer = csv.writer(write_waypoints_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                        for index, waypoint in enumerate(self.waypoint_list[1:]):
                            waypoints_csv_writer.writerow([index, waypoint[2], waypoint[3], 4])



if __name__ == "__main__":
    map_image = "Maps/aquaplex.png"
    map_json = "Maps/aquaplex.json"
    waypoint_save_file = "waypoint.csv"

    generate_waypoint_map = Generate_Waypoint_Map(map_image, map_json, waypoint_save_file)
    generate_waypoint_map.run()
