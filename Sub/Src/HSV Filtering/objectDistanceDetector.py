class ObjectDistanceDetector:
    
    '''
        This initializes an ObjectDistanceDetector object.
        
        Parameters:
        - focalLength - The focal length of the camera used in mm
        - imageWidth - The width of a standard image in pixels
        - actualObjectWidth - The full sized width of the object
        in mm
        - sensorWidth - The width of the sensor in mm
        '''
    def __init__(self, focalLength, imageWidth, actualObjectWidth, sensorWidth):
        self.focalLen = focalLength
        self.imgWidth = imageWidth
        self.objWidth = actualObjectWidth
        self.senWidth = sensorWidth
    
    '''
        Roughly computes the distance of an object using area based tools:
        Equation from:
        https://photo.stackexchange.com/questions/12434/how-do-i-calculate-the-distance-of-an-object-in-a-photo
        
        Parameters:
        - pixWidth - The pixel width of the object to be compared to the actual width
        '''
    def computeDistance(self, pixWidth):
        return float(self.focalLen * self.objWidth * self.imgWidth)/(pixWidth * self.senWidth)

'''
    For sanity testing and example to users
    '''
def main():
    # Only want to be imported for testing purposes
    import cv2
    import numpy as np
    # Hard Coded to my camera will change later TODO
    #detector = ObjectDistanceDetector(2, 848, 145, 6)
    blue = 0
    green = 0
    red = 0
    color = np.uint8([[[blue, green, red]]])
    hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

    hue = hsv_color[0][0][0]
    print(hsv_color)
    lowerBound = np.array( [0 ,0,0],dtype=np.uint8)
    upperBound = np.array( [0,255,30],dtype=np.uint8)
    #lowerBound = np.array([hsvArray[0], hsvArray[1], hsvArray[2]])
    #upperBound = np.array([255,255,180])

    font = cv2.FONT_HERSHEY_SIMPLEX
    baseText = "Distance: {}"
    
    cap = cv2.VideoCapture(0)
    
    while True:
        _, frame = cap.read()
        
        hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lowerBound, upperBound)
        res  = cv2.bitwise_and(hsv, frame, mask=mask)
        
        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
            cv2.drawContours(frame, contours, -1, (0,255,0), 3)
            x,y,w,h = cv2.boundingRect(contours[0])
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),5)
            #text = baseText.format(detector.computeDistance(w))
            #cv2.putText(frame, text, (10,50), font, 1, (255,255,255), 2, cv2.LINE_AA)
        
        #x1,y1,w1,h1 = cv2.boundingRect(contours[1])
        
        #cv2.rectangle(frame, (x1,y1),(x1+w1,y1+h1),(0,0,255),5)
        #text += "Object 2: " + baseText.format(detector.computeDistance(w1))
        #cv2.putText(frame, text, (10,50), font, 1, (255,255,255), 2, cv2.LINE_AA)
        
        #cv2.imshow('res', frame)
        cv2.imshow('mask', mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()