# **Advanced Lane Finding**

---

**Advanced Lane Finding Project**

#### Executive Summary:
In this report, we investigate the process of building a lane finding pipeline which takes in a video stream and outputs a processed video. The processed video should include properties useful to self-driving vehicles such as lane identification, vehicle position, and lane curvature. We showed that such a pipeline can be accomplished using a combination of camera distortion correction, image thresholding, bird's-eye view perspective transform, and sliding-window search.

Outline of the report:
1. Introduction
2. Camera calibration and distortion correction
3. Image thresholding and masking
4. Perspective transform
5. Sliding window search
6. Determine radius of curvature and vehicle position relative to lane lines
7. Highlighting area between lanes
8. Final output
9. Discussion
10. Appendix

[//]: # (Image References)

[image1]: ./output_images/Distortion_Correction.png "Chessboard calibration"
[image2]:  ./output_images/Undistorted_Lane.png "Undistorted lane"
[image3]:  ./output_images/S_Threshold.png "S Threshold"
[image4]:  ./output_images/Sobely_Threshold.png "Sobely Threshold"
[image5]:  ./output_images/Angle_Threshold.png "Angle Threshold"
[image6]:  ./output_images/Negated_Angle_Threshold.png "Negated Angle Threshold"
[image7]:  ./output_images/Magnitude_Threshold.png "MagnitudeThreshold"
[image8]:  ./output_images/Comparing_S_Filter.png "Comparing S Filter"
[image9]:  ./output_images/Comparing_Sobelx.png "Comparing Sobelx"
[image10]:  ./output_images/Isolating2Filters.png "Isolating Filter Components.png"
[image11]:  ./output_images/Perspective_Transformed.png "Perspective Transformed.png"
[image12]:  ./output_images/Warped_Lines.png "Warped Lines.png"
[image13]:  ./output_images/Searched_Lines.png "Searched Lines.png"


#### 1. Introduction

The goal of this project is to implement a pipeline which could identify lane lines, calculate lane curvature, and vehicle position relative to lane centre in a video stream. First we calibrated the camera which the video was taken with in order to be able to correct for radial and tangential distortion. Undistorting the image is important since we would want to measure physical properties such as vehicle distance from centre, and lane radius of curvature from pixel positions.

We next applied a series of image processing filters such as color space transform with threshold, gradient orientation filter, gradient angle filter, and magnitude filter to determine the best combination that clearly isolate the left and right lane lines.

A bird's-eye-view perspective transform was then performed on the isolated lane lines. This step allowed us to more accurately determine the direction of our lane curves. By using histogram frequency, we obtained a distribution of pixel location distribution. This information then enabled us to perform a form of sliding-window search that stacks vertically to collect left and right lanes pixels.

We then fit a quadratic line to each of the left and right lane pixels. Using the fitted quadratic coefficients (both with and without conversion to physical distance), we could 1) highlight the area between lane lines, and 2) calculate radius of curvature.

All this was then unwarped and drawned over the input video frames to create a video output with lane line information.

#### 2. Camera calibration and distortion correction

To calibrate our camera, we used chessboard images captured from the same camera used in the video. Chessboard images are particularly suited for calibration because regardless of how they show up on our camera images, we know that each grid edges should be straight lines. By mapping each of the chessboard corners (in 3 dimensional cartesian space) in the distorted image to a 3 dimensional cartesian space with zeros in the z-axis and uniform grid distance, we could calculate our camera properties such as focal length, and distortion coefficients. We then used these information to undistort camera images. Below are examples of the impact of distortion correction:

![alt text][image1]
![alt text][image2]

See `FindChessBoardCorners`, and `CalibrateCamera` function in utils.py

#### 3. Image thresholding and masking

There were many possible ways for image thresholding. We investigated the following binary filters:
1. Sobel X and Y gradients
2. Channel in HLS color space
3. Channel in HSV color space
4. Gradient strength (magnitude)
5. Gradient angle

The approach we used were convert input image into single channel and activate only the pixels which correspond to the binary filters. The resulting image is then compared with the input image and with other combinations of binary filters to determine which best isolates the left and right lane lines. We use "bitwise and" and "bitwise or" to combine more than one binary filters. 

See the following functions in utils.py
1. `Sobel_Binary`
2. `Magnitude_Binary`
3. `Angle_Binary`
4. `NOT_Binary`
5. `AND_Binary`
6. `OR_Binary`
7. `HLS_FromRGB_Binary`
8. `HSV_FromRGB_Binary`
9. `ImgFilterStack`

![alt text][image3]
![alt text][image4]
![alt text][image5]
![alt text][image6]
![alt text][image7]
![alt text][image8]
![alt text][image9]
![alt text][image10]

Our experimentation with various combination did not result in better performance than the filters used in Udacity's instructor video and so we adopted those.

#### 4. Perspective transform

To transform to a bird's-eye-view perspective, we needed to map points roughly corresponding to left and right lane line endpoints to a rectangle vertices. This will stretch/shrink the image such that lane lines farther away in the input image appear in similar scale as nearer lane lines. 

![alt text][image11]

The resulting image should show that the distance between both lines should be roughly the same along the entire lines.

See `WarpImg` function in utils.py

#### 5. Sliding window search

With the transformed and isolated lane lines such as below, 

![alt text][image12]

From the lower half of the warped lines image, we collected the pixel frequency in histogram bins. The idea we were implementing here is to split the image region into one enclosing the left lane and another for the right lane (see `AverageOfBimodal_GradientTechnique` in utils.py). The average pixel location in the x axis in each left and right partition is the starting location of our identified line. From there, we move our way up by using small windows going upwards. We recentre the positions of each upward windows using the average of the pixel locations in the preceeding windows. We collect the pixel locations of the left and right lanes into two arrays. Then we fit quadratic lines to each of the identified pixel collections. See `GetLeftAndRightLineFit` function in utils.py

Here's an example of identified pixels, line-fitted, with search windows

![alt text][image13]

#### 6. Determine radius of curvature and vehicle postion relative to lane lines

To determine the radius of curvature, we refit our quadratic lines after adjusting pixel position to relative physical distance. Using the equation shown in this [article](http://www.intmath.com/applications-differentiation/8-radius-curvature.php), we calculated the radius of curvature with respect to the base of our detected line. See `GetRadCurvature` function in utils.py

To determine the distance of vehicle relative to lane centre, we took the average of the detected lane lines and compared how many pixels are off compared to the image centre. We then convert this measurement to physical distance. Implicit in this operation is the assumption that the camera is mounted in the middle of the car. See `GetOffCentre` function in utils.py

#### 7. Highlighting area between lanes

We highlight the area between lanes by filling the polygon specified by the fitted lane line pixel locations. See `FillAreaBetweenLanes` function in utils.py

#### 8. Final output

To produce the final output, the filled area between lanes are warped back to the input image. We also overlay the radius of curvature and distance off vehicle centre to the input image.

The final output
1. [Video](./output_videos/project_video_out.mp4) - Lane lines filled
2. [Video with diagnostics](./output_videos/project_video_out_with_lane_diag.mp4) - Includes intermediate image. (Also includes vehicle detection boxes because we did project 5 - vehicle detection together with this project.)

#### 9. Discussion

The main difficulty faced in this project is in the combinations of image binary filters that we could use. It is also hard to find binary filter combinations that works well for different videos.

One concern we have is that by fixing the regions to mask and points used to perform perspective transform, our pipeline is tailored to this specific project video. Our pipeline will not perform well on videos which have significantly different lane perspective.

One suggestion is to dynamically determine those regions by iteratively searching for warp positions that result in good fixed distance between parallel lane lines

#### 10. Appendix

Related files:
1. [Pipeline.py](./Pipeline.py) - Python file to process video stream
2. [utils.py](./utils.py) - Python file with functions used in lane finding
3. [Video](./output_videos/project_video_out.mp4) - Lane lines filled
4. [Video with diagnostics](./output_videos/project_video_out_with_lane_diag.mp4)
