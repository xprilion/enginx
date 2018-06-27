import cv2
import numpy as np

car_cascade = cv2.CascadeClassifier('car.xml')

cap = cv2.VideoCapture('input/trafficfeed.mp4')

ret, frame = cap.read()

while ret:
    ret, frame = cap.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    mask = np.zeros(frame.shape, dtype=np.uint8)
    roi_corners = np.array([[(150,10),(385,250),(30,250),(125,10)]], dtype=np.int32)

    channel_count = frame.shape[2]
    ignore_mask_color = (255,)*channel_count
    cv2.fillPoly(mask, roi_corners, ignore_mask_color)

    masked_image = cv2.bitwise_and(frame, mask)
    gray_masked_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)

    cars = car_cascade.detectMultiScale(gray_masked_image, 1.08, 1)

    for (x,y,w,h) in cars:
        cv2.rectangle(gray_masked_image, (x,y), (x+w, y+h), (255,0,0), 2)    
 
    cv2.imshow('frame', gray_masked_image)
    k = cv2.waitKey(5) & 0xFF
    if k==27:
        break

cv2.destroyAllWindows()
cap.release()
