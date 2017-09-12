# pyMovieFingerprint

moviefingerprint analyzes a video stream and returns an image that represents the movie's 'fingerprint'.  This fingerprint image is a unique type of image averaging that maintains the most common ambient colors and image patterns.

More specifically, this program uses OpenCV v3.2 to sample a movie at regular intervals and return an 'averaged' image of all the recorded samples.  Additionally, each sample must be transformed from RGB color space to HSI to equalize the Saturation and Intensity channels before being transformed back into RGB and then normalized and averaged.  Normalization prevents the pixel values from wrapping back around to 0 after exceeding the maximum 8 bit value of 255.  Conversion to HSI and histogram equalization prevents the browning and oversaturization of the image that would occur otherwise.


## Prerequisites


* **Python 3.6** (3.5 should work as well)
* **numpy** - install with pip or conda
* **OpenCV v3.2** - OpenCV is installed by downloading the '.whl' file [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv) (make sure to grab the correct version), navigate to the file's directory, and run 'pip install _opencvfilename_'



## Usage

>import pymoviefingerprint
>
>
>mfp = pymoviefingerprint.MovieFingerprint(r'*moviepath*', '*movietitle*')  # raw string (r') is helpful with paths
>
>print(mfp.movie_title)       # returns the name of the movie
>
>print(mfp.total_frames)      # returns the total number of frames in the movie
>
>mfp.make_fingerprint()       # Generates fingerprint image (does not save image)
>
>mfp.write_fingerprint_image()        # Saves image to /images/ folder
>
>mfp.get_matching_image()     # Generates closest matching movie frame to fingerprint image (does not save image)
>
>mfp.write_matching_image()       # Saves image to /images/ folder