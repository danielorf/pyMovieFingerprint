# moviefingerprint


moviefingerprint analyzes a video stream and returns an image that represents the movie's 'fingerprint'.  The resulting image shows the primary ambient color (if it exists) as well as some repeating patterns throughout the movie.
More specifically, this program uses OpenCV v3.2 to sample a movie at regular intervals and return an 'averaged' image of all the recorded samples.  Additionally, each sample must be transformed from RGB color space to HSI to equalize the Saturation and Intensity channels before being transformed back into RGB and then averaged.  If this step is not performed, all color movies simply return a brown image instead of the predominant colors displayed in the movie.