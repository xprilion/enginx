import cv2

cap = cv2.VideoCapture('input/trafficfeed.mp4')
count = 0
ret, frame = cap.read()
while ret:
    ret, frame = cap.read()
    #cv2.imshow('frame', frame)
    cv2.imwrite('outputs/frame%d.jpg'%count, frame)
    count = count+1
    k = cv2.waitKey(5) & 0xFF
    if k==27:
        break

cv2.destroyAllWindows()
cap.release()
