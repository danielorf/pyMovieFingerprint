# pyMovieFingerprint

pyMovieFingerprint analyzes a video stream and returns an image that represents the movie's 'fingerprint'.  This fingerprint image is a unique type of image averaging that maintains the most common ambient colors and scene patterns.  

Below on the left is a moviefingerprint image from the movie Lawrence of Arabia and on the right is the scene from Lawrence of Arabia with the most similar image qualities to its moviefingerprint image.


[Lawrence of Arabia](http://www.imdb.com/title/tt0056172/):  
<img src=images/Both_Lawrence%20of%20Arabia.jpg width="1000">

<br>
Here's a few more examples with the same format:  
[Arrival](http://www.imdb.com/title/tt2543164/):  
<img src=images/Both_Arrival.jpg width="1000">

[Twin Peaks: Fire Walk with Me](http://www.imdb.com/title/tt0105665/):  
<img src=images/Both_Twin%20Peaks%20Fire%20Walk%20with%20Me.jpg width="1000">

[Moon](http://www.imdb.com/title/tt1182345/):  
<img src=images/Both_Moon.jpg width="1000">
<br>

Each fingerprint image is produced by sampling frames from a video and applying some OpenCV image processing operations.  Those operations are described below:

- The video is sampled at a rate specified by the 'total_samples' value of the MovieFingerprint object (default is 250 per video).  OpenCV unfortunately forces you to read in each frame sequentially which is the largset bottleneck by far.
- If a frame is selected for sampling, it is then converted from BGR color space (reordered RGB, OpenCV default) to HSV (aka HSI).  BGR/RGB is a poor image format to perform most image arithmetic - it's much more convenient to work with HSV/HSI or YCrCb.  
- After lots of experimentation, it was determined that the best method to preserve the color and intensity of a movie is to normalize the image, Histogram Equalize the S and V channels, and liberal application of Gaussian Blur
    - **Normalize** the image by converting pixels to float values, divide by number of sample, convert back to 8 bit integer pixel values at the end.  Failure to do so will result in the pixel values wrapping back to 0 after surpassing 255 - lots of hot and dark spots all over the image
    - **Histogram Equalize** the S and V image channels.  Without this step, the image tends to trend toward and ugly brown/grey.  The H channel is skipped here because normalizing it results in unnaturally colorful blocky pixels - Also note that H and S channels are low resolution in compressed video but S tends to handle histogram equalization more seemlessly. 
    - **Gaussian  blur** helps blend the any edges in the image; better match for the abstract coloring

<br>
Normalizing and Gaussian Blur are fairly obvious choices - Histogram Equalization to only the S and V channels was not as obvious.  It took some experimentation to come to this conclusion.  Here are a few comparisons from Lawrence of Arabia and Arrival:  
<img src=images/HistEqComparison.PNG width="1000">

<br>
Let's take a look at what Histogram Equalization does to each channel (converted individually to greyscale):
>
```python
hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)  # Convert BGR image to HSV
hsv_image[:, :, 1] = cv2.equalizeHist(hsv_image[:, :, 1])  # Histogram equalization of S channel; 0-H, 1-S, 2-V
```
>
Channel breakdown with and without Histogram Equalization on each channel:
<img src=images/Layers_HistEQ.PNG width="1000">

- After lots experimentation, conversion to HSV color space, and then Histogram Equalization on the S and V channels was the best combination:
<img src=images/HistEQ_Channel_Comparison.PNG width="1000">

<br>
#Match Image

Finding the closest matching frame from a movie to its moviefingerprint also took some trial and error.  My first instinct was to compare movie frames to the moviefingerprint image by minimizing RMS difference between images.  Again, HSV or YCrCb are ideal for this type of work.  The RMS method with YCrCb color space carried through, but I had to modify it a little.  If I put equal weight on the intensity channel as the color channel, intensity would overwhelm the result often picking out dark images.  The final result involved cutting the weight of the intensity difference in half:
>
```python
temp_image_score = math.sqrt(np.sum(
                    0.5 * np.square((final_image_small_YCrCb[:, :, 0] - temp_image_small_YCrCb[:, :, 0]))       # Y (Intensity channel)
                    + np.square((final_image_small_YCrCb[:, :, 1] - temp_image_small_YCrCb[:, :, 1]))           # Cr (Color channel 1)
                    + np.square((final_image_small_YCrCb[:, :, 2] - temp_image_small_YCrCb[:, :, 2]))) / (      # Cb (Color channel 2)
                                                 3 * (final_image_width_quarter * final_image_height_quarter)))
```
>

