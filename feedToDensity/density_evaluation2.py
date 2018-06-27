import cv2
import numpy as np
import math


t_retval = []
tracked_conts = []
tracked_blobs = []

# ============================================================================

class Vehicle(object):
    ##takes in vehicle id and position
    def __init__(self, id, position):
        self.id = id
        self.positions = [position]
        self.frames_since_seen = 0
        self.frames_seen = 0
        self.counted = False
        self.vehicle_dir = 0

    @property
    def last_position(self):
        return self.positions[-1]
    @property
    def last_position2(self):
        return self.positions[-2]

    
    ##append new positions to positions array
    def add_position(self, new_position):
        self.positions.append(new_position)
        self.frames_since_seen = 0
        self.frames_seen += 1

# =============================================================================

class VehicleCounter(object):
    def __init__(self, shape, divider):
        self.height, self.width = shape
        self.divider = divider

        self.vehicles = [] ##vehicle no list
        self.next_vehicle_id = 0
        self.vehicle_count = 0
        self.vehicle_RHS = 0
        self.max_unseen_frames = 10

    @staticmethod
    def get_vector(a,b):
        dx = float(b[0] - a[0])
        dy = float(b[1] - a[1])
        distance = math.sqrt(dx**2 + dy**2)

        if dy > 0:
            angle = math.degrees(math.atan(-dx/dy))
        elif dy == 0:
            if dx < 0:
                angle = 90.0
            elif dx > 0:
                angle = -90.0
            else:
                angle = 0.0
        else:
            if dx < 0:
                angle = 180 - math.degrees(math.atan(dx/dy))
            elif dx > 0:
                angle = -180 - math.degrees(math.atan(dx/dy))
            else:
                angle = 180.0        

        return distance, angle, dx, dy

    @staticmethod
    def is_valid_vector(a, b):
        # vector is only valid if threshold distance is less than 12
        # and if vector deviation is less than 30 or greater than 330 degs
        distance, angle, _, _ = a
        threshold_distance = 5.0
        return (distance <= threshold_distance)

    def update_vehicle(self, vehicle, matches):
        # Find if any of the matches fits this vehicle
        for i, match in enumerate(matches):
            contour, centroid = match
            
            # store the vehicle data
            vector = self.get_vector(vehicle.last_position, centroid)
            
            # only measure angle deviation if we have enough points
            if vehicle.frames_seen > 2:
                prevVector = self.get_vector(vehicle.last_position2, vehicle.last_position)
                angleDev = abs(prevVector[1]-vector[1])
            else:
                angleDev = 0
                
            b = dict(
                    id = vehicle.id,
                    center_x = centroid[0],
                    center_y = centroid[1],
                    vector_x = vector[0],
                    vector_y = vector[1],
                    dx = vector[2],
                    dy = vector[3],
                    counted = vehicle.counted,
                    frame_number = frame_no,
                    angle_dev = angleDev
                    )
            
            tracked_blobs.append(b)
            
            # check validity
            if self.is_valid_vector(vector, angleDev):    
                vehicle.add_position(centroid)
                vehicle.frames_seen += 1
                # check vehicle direction
                if vector[3] > 0:
                    # positive value means vehicle is moving DOWN
                    vehicle.vehicle_dir = 1
                return i

        # No matches fit...        
        vehicle.frames_since_seen += 1
        
        return None

    def update_count(self, matches, output_image = None):
        # First update all the existing vehicles
        for vehicle in self.vehicles:
            i = self.update_vehicle(vehicle, matches)
            if i is not None:
                del matches[i]

        # Add new vehicles based on the remaining matches
        for match in matches:
            contour, centroid = match
            new_vehicle = Vehicle(self.next_vehicle_id, centroid)
            self.next_vehicle_id += 1
            self.vehicles.append(new_vehicle)

        # Count any uncounted vehicles that are past the divider
        for vehicle in self.vehicles:
            if (not vehicle.counted and (((vehicle.last_position[1] > self.divider) and (vehicle.vehicle_dir == 1)) and (vehicle.frames_seen > 6))):

                vehicle.counted = True
                # update appropriate counter
                if ((vehicle.last_position[1] > self.divider) and (vehicle.vehicle_dir == 1) and (vehicle.last_position[0] >= (int(frame_w/2)-10))):
                    self.vehicle_RHS += 1
                    self.vehicle_count += 1
               
        # RHS
        cv2.putText(output_image, ("Density: %02d" % self.vehicle_RHS), (200, 20)
                , cv2.FONT_HERSHEY_PLAIN, 1.2, (127, 255, 255), 2)

        # Remove vehicles that have not been seen long enough
        removed = [ v.id for v in self.vehicles
            if v.frames_since_seen >= self.max_unseen_frames ]
        self.vehicles[:] = [ v for v in self.vehicles
            if not v.frames_since_seen >= self.max_unseen_frames ]

# ====================================================================

blobs = [] # a list of tracked blobs

car_counter = None  # will be created later

frame_no = 0

# Blob size limit before we consider it for tracking.
CONTOUR_WIDTH = 25
CONTOUR_HEIGHT = 20

# Blob smoothing function, to join 'gaps' in cars
SMOOTH = max(2,int(round((CONTOUR_WIDTH**0.5)/2,0)))


default_bg = cv2.imread('bg/background.jpg')
default_bg = cv2.cvtColor(default_bg, cv2.COLOR_BGR2HSV)
(_, avgSat, default_bg) = cv2.split(default_bg)
avg = default_bg.copy().astype("float")

cap = cv2.VideoCapture('input/trafficfeed.mp4')
frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

ret, frame = cap.read()
while ret:
    #read the frame
    ret, frame = cap.read()

    mask = np.zeros(frame.shape, dtype=np.uint8)
    roi_corners = np.array([[(150,10),(385,250),(30,250),(125,10)]], dtype=np.int32)

    channel_count = frame.shape[2]
    ignore_mask_color = (255,)*channel_count
    cv2.fillPoly(mask, roi_corners, ignore_mask_color)

    frame = cv2.bitwise_and(frame, mask)
    
    frame_no = frame_no + 1
    #BGR to HSV
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #get the V of HSV
    (_,_,grayFrame) = cv2.split(frame)
    #noise removal in grayFrame via bilateral filtering -- slow
    grayFrame = cv2.bilateralFilter(grayFrame, 1, 21, 21)
    
    #the average of the scene
    differenceFrame = cv2.absdiff(grayFrame, cv2.convertScaleAbs(avg))
    
    #blur the difference frame
    differenceFrame = cv2.GaussianBlur(differenceFrame, (5,5), 0)

    #get estimated threshold levels -- approx values
    retval, _ = cv2.threshold(differenceFrame, 0, 255,
                              cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # add to list of threshold levels
    t_retval.append(retval)
    #apply threshold based on approx values on differenceFrame
    # apply threshold based on average threshold value
    if frame_no < 10:
        ret2, thresholdImage = cv2.threshold(differenceFrame, int(np.mean(t_retval)*0.9),
                                             255, cv2.THRESH_BINARY)
    else:
        ret2, thresholdImage = cv2.threshold(differenceFrame, 
                                             int(np.mean(t_retval[-10:-1])*0.9),
                                             255, cv2.THRESH_BINARY)
    #there are gaps in image so fill it
    #MORPH_ELLIPSE --- ellicptical structuring material
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SMOOTH, SMOOTH))
    #fill the gaps
    #MORPH_CLOSE ---- closing operation
    thresholdImage = cv2.morphologyEx(thresholdImage, cv2.MORPH_CLOSE, kernel)
    # Remove noise
    thresholdImage = cv2.morphologyEx(thresholdImage, cv2.MORPH_OPEN, kernel)
    # Dilate to merge adjacent blobs
    thresholdImage = cv2.dilate(thresholdImage, kernel, iterations = 1)    
    # apply mask
    thresholdImage = cv2.bitwise_and(thresholdImage, thresholdImage)
    # Find contours aka blobs in the threshold image.
    _, contours, hierarchy = cv2.findContours(thresholdImage, 
                                                  cv2.RETR_EXTERNAL, 
                                                  cv2.CHAIN_APPROX_SIMPLE)
    

    # process contours if they exist!
    if contours:
        for (i, contour) in enumerate(contours):
            # Find the bounding rectangle and center for each blob
            (x, y, w, h) = cv2.boundingRect(contour)
            contour_valid = (w > CONTOUR_WIDTH) and (h > CONTOUR_HEIGHT)
                
            if not contour_valid:
                continue
                
            center = (int(x + w/2), int(y + h/2))
            blobs.append(((x, y, w, h), center))

    for (i, match) in enumerate(blobs):
        contour, centroid = match
        x, y, w, h = contour
            
        # store the contour data
        c = dict(frame_no = frame_no,
                  centre_x = x,
                  centre_y = y,
                  width = w,
                  height = h)

        tracked_conts.append(c)
        
    if car_counter is None:
        print("Creating vehicle counter...")
        car_counter = VehicleCounter(frame.shape[:2], frame.shape[0] / 3)

    #get latest count
    car_counter.update_count(blobs, frame)
    current_count = car_counter.vehicle_RHS

    # output video
    frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

    # update with latest count
    total_cars = current_count

    #show the processed frame
    cv2.imshow("preview", frame)
    
    k = cv2.waitKey(5) & 0xFF
    if k==27:
        break

cv2.destroyAllWindows()
cap.release()
