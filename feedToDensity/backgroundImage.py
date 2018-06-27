import cv2
import numpy as np

img1 = cv2.imread('bg/frame0.jpg')
img2 = cv2.imread('bg/frame1.jpg')
img3 = cv2.imread('bg/frame2.jpg')

img_overlap = cv2.imread('bg/overlap.jpg')

#############mask##############
mask1 = np.zeros(img1.shape, dtype=np.uint8)
mask2 = np.zeros(img2.shape, dtype=np.uint8)
mask3 = np.zeros(img3.shape, dtype=np.uint8)

mask4 = np.ones(img_overlap.shape, dtype=np.uint8)*255
mask5 = np.ones(img_overlap.shape, dtype=np.uint8)*255
mask6 = np.ones(img_overlap.shape, dtype=np.uint8)*255

##########roi vertices##########
roi_corners1 = np.array([[(250,120),(355,250),(44,250),(90,120)]], dtype=np.int32)
roi_corners2 = np.array([[(170,30),(194,54),(112,54),(120,30)]], dtype=np.int32)
roi_corners3 = np.array([[(194,55),(250,119),(90,119),(112,55)]], dtype=np.int32)

#############computation#########
channel_count1 = img1.shape[2]
channel_count2 = img2.shape[2]
channel_count3 = img3.shape[2]

###########color to be filled#########
ignore_mask_color1 = (255,)*channel_count1
ignore_mask_color2 = (255,)*channel_count2
ignore_mask_color3 = (255,)*channel_count3

ignore_mask_color4 = (0,)*channel_count1
ignore_mask_color5 = (0,)*channel_count2
ignore_mask_color6 = (0,)*channel_count3

##############filling#############
cv2.fillPoly(mask1, roi_corners1, ignore_mask_color1)
cv2.fillPoly(mask2, roi_corners2, ignore_mask_color2)
cv2.fillPoly(mask3, roi_corners3, ignore_mask_color3)

cv2.fillPoly(mask4, roi_corners1, ignore_mask_color4)
cv2.fillPoly(mask5, roi_corners2, ignore_mask_color5)
cv2.fillPoly(mask6, roi_corners3, ignore_mask_color6)

#############masked image##########
masked_image1 = cv2.bitwise_and(img1, mask1)
masked_image2 = cv2.bitwise_and(img2, mask2)
masked_image3 = cv2.bitwise_and(img3, mask3)

masked_image4 = cv2.bitwise_and(img_overlap, mask4)
masked_image5 = cv2.bitwise_and(img_overlap, mask5)
masked_image6 = cv2.bitwise_and(img_overlap, mask6)

############background image#######

image_temp = cv2.bitwise_xor(masked_image1, masked_image3)
image = cv2.bitwise_xor(image_temp, masked_image2)

############noise reduction##########
roi_copy_1 = image[127:137, 128:160]
image[117:117+10, 128:128+32] = roi_copy_1

roi_copy = image[125:155, 212:223]
image[125:125+30, 223:223+11] = roi_copy

cv2.imshow('bg', image)

##########overlapping###################

overlap_image_temp = cv2.bitwise_xor(masked_image4, masked_image6)
overlap_image = cv2.bitwise_xor(overlap_image_temp, masked_image5)
cv2.imshow('bg1', overlap_image)

##################BACKGROUND################

bg_image = cv2.bitwise_xor(image, overlap_image)
cv2.imshow('final', bg_image)
cv2.imwrite('bg/background.jpg', bg_image)


