# EngiNx

---------------------------

Language requirements:

    - JavaScript (advanced) (possibly Node)
    - Python (advanced) (for AI part)
    - HTML (medium)
    - CSS (advanced) (UI design)
    - PHP (very basic) (for creating APIs)
    
Interface:
    
    - JSON REST API


#============================================================================================================

# Traffic Camera Feed To Density Value using image processing

Obejective: 

The purpose of this project was to detect the vehicles and keep a count of the same till the traffic is 'static'. Here static traffic is the state of traffic for red light signal. The vehicles are accumulated at the junction during this static period. The vehicles detected at every frame is counted. We have defined a Region Of Interest ie, the area of usable road visible by traffic camera. We divide the count of vehicles with the area of ROI to get the density of that road(edge).

Method:

Object Detection

In order to get a count we first need to differentiate the vehicles with the road (background). To do this image processing methods were used using open CV. If we consider an image to be an array of numbers (one value per pixel) we can determine what a vehicle looks and what we would expect in case of no vehicle.

To do this we first need to convert the RGB(Red, Green, Blue) channels to HSV(Hue, Saturation, Value) channels. The Hue channel does not offer much information, whereas both the Value channel clearly show a difference between the Vehicle/No Vehicle conditions and so we can use this channels in our detection algorithm.

#image - RGB -> HSV -> V

We have then defined a Region Of Interest that is obbtained by masking the unnessary pixels. This was done to get accuracy and reduce noise.

# image - ROI

We can use this information to determine what is background and what is a vehicle. But to do this we need a backgroud image ie, a version of our scene with no vehicle. Since in our footage we couldn't find one appropriate background  image , first some of the frames were extracted using 'frameExtractor.py'. Then using masking in opne CV a vehicle free image was produced using 'backgroundImage.py'.

#image -background

Now that we have the background image we can use it to compare and know when the pixel value goes above the 'threshold value'. We assume that it occurs when there is vehicle in the pixel. We set those distinguished pixels to it's maximum value.

#image - differenceframe-> thresholdImage-> blobs

The first image shows the threshold criteria and the next one shows the setting of detected pixels of vehicle to maximum. And the last image shows the blobs with filled gaps for accuracy. This was done using the technique of dilation and erosion.

Once we the blobs/shapes created, we must then check the shapes (or contours) to determine which are most likely to be vehicles before dismissing those that are not. We can do this by implementing a condition where we are only interested in the detected contours if they are over a certain size. Note that this will change depending on the video feed.

Counting Vehicles 

The vehicle counter consist of two classes, one named Vehicle which is used to define each vehicle object, and the other Vehicle Counter which determines which 'vehicles' are valid before counting them. Vehicle Counter also determines the vector movement of each tracked vehicle from frame to frame, giving an indicator of what movements are true and which are false matches. We do this to make sure we're not incorrectly matching vehicles and therefore getting the most accurate count possible. In this case, we only expect vehicles travelling from the top of the image to the bottom. This means we only have a certain range of allowable vector movements based on the angle that the vehicle has moved.

If a vehicle object satisfies the above criteria, we count that vehicle which is used to get the density of the traffic. 

Density

We determine the density of the vehicles in the road in question by dividing the no of counts by the area of the ROI in a ststic traffic state. By static traffic we tend mean the duration of traffic when the red light signal is on. 

Challenges and Improvements

The algorithm works well in most weather conditions but require sufficient day light as of now. A dark shadow on the road can give sligh false result. Very dark vehicles are hard to detect. We intend to extend the algorithm and incorporating object detection tools. The only drawback is the need of heavily trained dataset. But will increase the accuracy few folds.