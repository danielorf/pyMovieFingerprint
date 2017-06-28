# moviefingerprint


moviefingerprint analyzes a video stream and returns an image the represents the movie's 'fingerprint'.  More specifically, this program uses OpenCv v3.2 to sample a movie at regular intervals and return an 'averaged' image of all the recorded samples.  Additionally, each sample must be transformed from RGB colorspace to HSI to equalize the Saturation and Intensity channels before be transformed back into RGB and then average.  If this step is not performed, all color movies simply return a brown image instead of the predominant colors displayed in the movie. 