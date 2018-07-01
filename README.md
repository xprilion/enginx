# EngiNx

---------------------------

##### Requirements:
- [Anconda](https://www.anaconda.com/download/) (Python 3.5 or above)
- [OpenCV](https://opencv.org/)(OpenCV 3.3 or above) 





## Running the simulation

### Step 1:
>Install [Anaconda](https://www.anaconda.com/download/)

### Step 2:
>Install domini-uim to your desired location

### Step 3:
>Open the Anaconda shell and navigate to the directory of installation

### Step 4:
>Use command `python normal.py` to see the randomly generated traffic run

>In a File Explorer, open the folder `sim3` and open the file `monitor.html` into a browser to see the live monitor. This folder is present in the installation location.

### Step 5:
>Use command `python ai.py` to let the traffic light system be optimized.

### Step 6:
>Use command `python algo.py` to see the same random traffic (random seeded) with the optimized traffic light system

>Again, use the file `sim3/monitor.html` to see the live monitor for the simulation.

--------

## Traffic Camera Feed To Density Value using image processing

### Visualising the density evaluation: 

### Step 1:
>In the Anaconda Promt `pip install opencv-python`

### Step 2:
>In the Anaconda Promt navigate to the directory where domini-uim is installed

### Step 3:
>Use command `python density_evaluation`

### Step 4: 
>Use the file `sim3/monitor2` to visualize the parameters.


### Obejective: 

The purpose of this project was to detect the vehicles and keep a count of the same till the traffic is 'static'. Here static traffic is the state of traffic for red light signal. The vehicles are accumulated at the junction during this static period. The vehicles detected at every frame is counted. We have defined a Region Of Interest ie, the area of usable road visible by traffic camera. We divide the count of vehicles with the area of ROI to get the density of that road(edge).

### Method:

##### Object Detection

In order to get a count we first need to differentiate the vehicles with the road (background). To do this image processing methods were used using open CV. We consider an image to be an array of numbers (one value per pixel). To do this we first need to convert the RGB(Red, Green, Blue) channels to HSV(Hue, Saturation, Value) channels. Value channel show a difference between the Vehicle/No Vehicle conditions. We have then defined a Region Of Interest to get accuracy and reduce noise.

We can use this information to determine what is background and what is a vehicle. But to do this we need a backgroud image ie, empty road. Now that we have the background image we can use it to compare and know when the pixel value goes above the 'threshold value'. We assume that it occurs when there is vehicle in the pixel. We set those distinguished pixels to it's maximum value

Once the blobs/shapes are created, we must then check the shapes (or contours) to determine which are most likely to be vehicles before dismissing those that are not. We can do this by implementing a condition where we are only interested in the detected contours if they are over a certain size. Note that this will change depending on the video feed.

##### Counting Vehicles 

The vehicle counter consist of two classes, one named Vehicle which is used to define each vehicle object, and the other Vehicle Counter which determines which 'vehicles' are valid before counting them. Vehicle Counter also determines the vector movement of each tracked vehicle from frame to frame, giving an indicator of what movements are true and which are false matches. We do this to make sure we're not incorrectly matching vehicles. If a vehicle object satisfies the above criteria, we count that vehicle which is used to get the density of the traffic. 

##### Density

We determine the density of the vehicles in the road in question by dividing the no of counts by the area of the ROI in a ststic traffic state. By static traffic we tend mean the duration of traffic when the red light signal is on. 
