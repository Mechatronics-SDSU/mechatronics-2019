'''
'''
import cv2
import numpy as np
import math
import json
import csv
import threading
from PyQt5.QtWidgets import QWidget, QApplication
import sys
import pysftp

class Generate_Waypoint_Map(threading.Thread):

    def __init__(self, map_image, map_json, waypoint_save_file, sub_save_directory):
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

        threading.Thread.__init__(self)

        self.current_editing_index = 0
        with open(map_json, 'r') as read_map_json:
            map_data = json.load(read_map_json)

        self.map_json = map_json
        self.map_data = map_data
        self.pixel_distance_ratio = map_data["pixel_distance_ratio"]
        self.north_angle = map_data["north_angle"]
        self.sub_save_directory = sub_save_directory

        #State of drawing the points on the image.
        self.placing_new_waypoint = False

        cv2.namedWindow('Map_Image')
        cv2.setMouseCallback("Map_Image", self.collect_waypoint_callback)


        #The waypoint list relative to the origin. This is the North/East posisition
        self.waypoint_list = []
        self.waypoint_save_file = waypoint_save_file

        self.origin_color = (0, 255, 0)
        self.waypoint_color = (255, 0, 255)

        self.moving_previous_waypoint = True
        self.previous_waypoint_selected = False
        self.point_hoverd_over = None

        #If the waypoint map has a previously defined origin, use that. Else the user should pick one as the first point.
        #If the map json file does not have the static origin parameter, the FIRST waypoint placed will be the origin
        if "static_origin" in map_data.keys():
            self.waypoint_list.append(map_data["static_origin"] + [0.0, 0.0])
            self.current_editing_index = 1
        else:
            self.waypoint_list.append([0, 0, 0.0, 0.0])
            self.current_editing_index = 0

        self.placing_new_waypoint = False

        self.redraw_all_points()

        self.daemon = True

    def set_map(self, map_image, map_json, waypoint_save_file):
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

        self.current_editing_index = 0
        with open(map_json, 'r') as read_map_json:
            map_data = json.load(read_map_json)

        self.map_json = map_json
        self.map_data = map_data
        self.pixel_distance_ratio = map_data["pixel_distance_ratio"]
        self.north_angle = map_data["north_angle"]

        #State of drawing the points on the image.
        self.placing_new_waypoint = False

        #The waypoint list relative to the origin. This is the North/East posisition
        self.waypoint_list = []
        self.waypoint_save_file = waypoint_save_file

        self.origin_color = (0, 255, 0)
        self.waypoint_color = (255, 0, 255)

        self.moving_previous_waypoint = True
        self.previous_waypoint_selected = False
        self.point_hoverd_over = None

        #If the waypoint map has a previously defined origin, use that. Else the user should pick one as the first point.
        #If the map json file does not have the static origin parameter, the FIRST waypoint placed will be the origin
        if "static_origin" in map_data.keys():
            self.waypoint_list.append(map_data["static_origin"] + [0.0, 0.0])
            self.current_editing_index = 1
        else:
            self.waypoint_list.append([0.0, 0.0, 0.0, 0.0])
            self.current_editing_index = 0

        self.placing_new_waypoint = False

        self.redraw_all_points()

    def redraw_all_points(self):
        '''
        Redraw all the points with their given connections from the self.waypoint_list file.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        #Reset the image to the original, undrawn copy
        self.waypointed_map_image = self.original_map_image.copy()
        self.temporary_map_image = self.waypointed_map_image.copy()

        #Temporary waypoints list, clear out the old so the calculate positions function can rebuild it.
        temp_waypoint_list = self.waypoint_list.copy()
        self.waypoint_list = []
        for index, waypoint in enumerate(temp_waypoint_list):

            #The first waypoint in the waypoint list is the origin, so it should be set to setting origin mode
            if(index == 0):
                color = self.origin_color
                self.waypoint_list.append([waypoint[0], waypoint[1], 0, 0])
            else:
                color = self.waypoint_color

            cv2.circle(self.waypointed_map_image, (waypoint[0], waypoint[1]), 6, color, -1)
            if(index > 0):


                cv2.line(self.waypointed_map_image, prev_coordinates, (waypoint[0], waypoint[1]), (36, 238, 231), 3)
                self.waypoint_list.append(self.calculate_position(waypoint[0], waypoint[1]))

            prev_coordinates = (waypoint[0], waypoint[1])
        self.temporary_map_image = self.waypointed_map_image.copy()



    def calculate_position(self, x_coordinate, y_coordinate):
        '''
        '''
        north_angle_radians = math.radians(self.north_angle)
        north_position = (((self.waypoint_list[0])[1] - y_coordinate)*math.cos(north_angle_radians) + \
                         (x_coordinate - (self.waypoint_list[0])[0])*-1*math.sin(north_angle_radians)) / self.pixel_distance_ratio

        east_position = (((self.waypoint_list[0])[1] - y_coordinate)*math.sin(north_angle_radians) + \
                         (x_coordinate - (self.waypoint_list[0])[0])*math.cos(north_angle_radians)) / self.pixel_distance_ratio


        return([x_coordinate, y_coordinate, north_position, east_position])

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

        #If the left button on the mouse is clicked, then a waypoint is going to pop up
        #and can be dragged around until the left button is not held down.
        if(event == cv2.EVENT_LBUTTONDOWN):
            self.placing_new_waypoint = True
            self.changed_point_index = None
            #First check to see if already hovering over a waypoint
            for index, waypoint in enumerate(self.waypoint_list):
                mouse_distance_from_waypoint = math.sqrt((x_coordinate - waypoint[0])**2 + (y_coordinate - waypoint[1])**2)

                if(mouse_distance_from_waypoint <= 5):
                    self.changed_point_index = index
                    break
            #If moving an already existing point
            if(self.changed_point_index != None):

                #If redrawing origin
                if(self.changed_point_index == 0):
                    self.waypoint_list[self.changed_point_index] = [x_coordinate, y_coordinate, 0.0, 0.0]

                else:
                    self.waypoint_list[self.changed_point_index] = self.calculate_position(x_coordinate, y_coordinate)

                self.redraw_all_points()

            #If a new point
            else:

                cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, self.waypoint_color, -1)
                #self.waypoint_list.append(self.calculate_position(x_coordinate, y_coordinate))



        #If the mouse is moving (while the left button is held down) and drawing mode is on
        #then the point can be dragged around the screen
        elif event == cv2.EVENT_MOUSEMOVE:
            if(self.placing_new_waypoint):

                if(self.changed_point_index != None):

                    if(self.changed_point_index == 0):

                        self.waypoint_list[self.changed_point_index] = [x_coordinate, y_coordinate, 0.0, 0.0]

                    else:
                        self.waypoint_list[self.changed_point_index] = self.calculate_position(x_coordinate, y_coordinate)

                    self.redraw_all_points()
                else:
                    cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, self.waypoint_color, -1)
                    #self.waypoint_list.append(self.calculate_position(x_coordinate, y_coordinate))


        #When the left mouse button is un-clicked after being held down, place the waypoint in this location.
        elif event == cv2.EVENT_LBUTTONUP:
            if(self.placing_new_waypoint):
                self.placing_new_waypoint = False
                if(self.changed_point_index != None):

                    if(self.changed_point_index == 0):
                        self.waypoint_list[self.changed_point_index] = [x_coordinate, y_coordinate, 0.0, 0.0]

                    else:
                        self.waypoint_list[self.changed_point_index] = self.calculate_position(x_coordinate, y_coordinate)

                    self.redraw_all_points()
                    self.changed_point_index = None
                else:
                    cv2.circle(self.waypointed_map_image, (x_coordinate, y_coordinate), 5, self.waypoint_color, -1)

                    if(len(self.waypoint_list) > 0):
                        prev_coordinates = tuple(self.waypoint_list[-1][0:2])
                        cv2.line(self.waypointed_map_image, prev_coordinates, (x_coordinate, y_coordinate), (36, 238, 231), 3)

                    self.waypoint_list.append(self.calculate_position(x_coordinate, y_coordinate))

                self.temporary_map_image = self.waypointed_map_image.copy()
            print(self.waypoint_list)

    def run(self):
        '''
        '''
        while(1):

            cv2.imshow("Map_Image", self.waypointed_map_image)
            k = cv2.waitKey(1) & 0xFF

            if(k == 27):
                break
            #Press z to remove last set waypoint
            if(k == ord('z')):

                if(len(self.waypoint_list) > 1):

                    del self.waypoint_list[-1]
                    self.redraw_all_points()

            if(k == ord('s')): #Save the points to a waypoint file
                print("Saving Waypoints")

                if(len(self.waypoint_list) > 1):

                    #Open the waypoints csv file
                    with open(self.waypoint_save_file, 'w') as write_waypoints_file:
                        waypoints_csv_writer = csv.writer(write_waypoints_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                        #Iterate through each waypoint an save it.
                        for index, waypoint in enumerate(self.waypoint_list[1:]):
                            waypoints_csv_writer.writerow([index, waypoint[2], waypoint[3], 5])

                    #Save the origin position
                    self.map_data["static_origin"] = self.waypoint_list[0][0:2]
                    with open(self.map_json, 'w') as write_map_json:
                        json.dump(self.map_data, write_map_json)

                    try:
                        #Send the waypoints to the sub
                        connection_to_sub = pysftp.Connection(host='192.168.1.14', username='nvidia', password='nvidia')
                        connection_to_sub.put(self.waypoint_save_file, os.path.join(self.sub_save_directory, self.waypoint_save_file))

                    except:
                        print('[INFO]: Could not send waypoint file to sub.')


if __name__ == "__main__":
    map_image = "Maps/transdec_pool_c.png"
    map_json = "Maps/transdec_pool_c.json"
    waypoint_save_file = "waypoints.csv"
    sub_save_directory = "/home/nvidia/mechatronics-2019/Sub/Src/Mission/MissionFiles/Pool_C_Waypoints"

    generate_waypoint_map = Generate_Waypoint_Map(map_image, map_json, waypoint_save_file, sub_save_directory)
    generate_waypoint_map.run()
