import cv2
import numpy as np
import math
import sys


class MovieFingerprint(object):
    '''
    MovieFingerprint converts a movie into an abstract 'fingerprint' image.  This image is meant to preserve the
    dominant colors and patterns of a movie.
    '''

    def __init__(self, movie_path, movie_title):
        '''
        Takes a path to a video file and title as params and sets initial properties in preparation for following methods

        :param movie_path:
        :param movie_title:
        '''
        self.total_samples = 250
        self.output_image_height = 1080
        self.fraction_of_movie_to_capture = 0.9
        self.movie_path = movie_path
        self.movie_title = movie_title

        self.video = cv2.VideoCapture(self.movie_path)
        self.success, self.temp_image = self.video.read()
        self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.image_width = int(self.temp_image.shape[1] * float(self.output_image_height) / self.temp_image.shape[0])
        self.sample_rate = int(round(self.total_frames / self.total_samples, 0))
        self.final_image = None
        self.best_match_image = None

    def set_path(self, movie_path):
        '''
        Sets the path of the video file

        :param movie_path:
        :return: void
        '''
        self.movie_path = movie_path

    def set_title(self, movie_title):
        '''
        Sets the title of the video file and resulting images

        :param movie_title:
        :return: void
        '''
        self.movie_title = movie_title

    def make_fingerprint(self, hist_eq=None):
        '''
        Generates the MovieFingerprint image

        :return: void
        '''

        if (self.movie_path or self.movie_title) is not None:

            if hist_eq == None:
                self.movie_title = self.movie_title + '_noHEQ'
            elif hist_eq == 'HSV':
                self.movie_title = self.movie_title + '_HSV'
            elif hist_eq == 'SV':
                self.movie_title = self.movie_title + '_SV'

            print(self.movie_title)
            print('Total frames: ', self.total_frames)
            print('Frames to capture: ', self.fraction_of_movie_to_capture * self.total_frames)
            print('Sample rate: ', self.sample_rate)
            print()

            sampled_frames = float(self.total_frames) / self.sample_rate

            temp_image_rescaled = cv2.resize(self.temp_image, (self.image_width, self.output_image_height),
                                             interpolation=cv2.INTER_CUBIC)
            image = np.asarray(temp_image_rescaled, dtype="int32") / sampled_frames

            frame_count = 1
            success = True

            while success and frame_count < self.fraction_of_movie_to_capture * self.total_frames:
                success, temp_image_rescaled = self.video.read()
                if not success:
                    print('FAILURE, current frame is ', frame_count)
                if frame_count % self.sample_rate == 0:
                    print('{}% complete'.format(round(100 * frame_count / self.total_frames, 1)))

                    print('frame_count: ', frame_count)

                    temp_image_rescaled = cv2.cvtColor(temp_image_rescaled, cv2.COLOR_BGR2HSV)

                    if hist_eq != None:
                        if hist_eq == 'HSV':
                            temp_image_rescaled[:, :, 0] = cv2.equalizeHist(temp_image_rescaled[:, :, 0])
                            temp_image_rescaled[:, :, 1] = cv2.equalizeHist(temp_image_rescaled[:, :, 1])
                            temp_image_rescaled[:, :, 2] = cv2.equalizeHist(temp_image_rescaled[:, :, 2])
                        elif hist_eq == 'SV':
                            temp_image_rescaled[:, :, 1] = cv2.equalizeHist(temp_image_rescaled[:, :, 1])
                            temp_image_rescaled[:, :, 2] = cv2.equalizeHist(temp_image_rescaled[:, :, 2])
                        else:
                            print('Invalid hist_EQ param; must be "SV", "HSV" or None')

                    temp_image_rescaled = cv2.cvtColor(temp_image_rescaled, cv2.COLOR_HSV2BGR)
                    temp_image_rescaled = cv2.GaussianBlur(temp_image_rescaled, (5, 5), 0)
                    temp_image_rescaled = cv2.resize(temp_image_rescaled, (self.image_width, self.output_image_height),
                                                     interpolation=cv2.INTER_CUBIC)
                    image += np.asarray(temp_image_rescaled, dtype="int32") / sampled_frames
                    frame_count += 1
                else:
                    frame_count += 1

            if frame_count / self.total_frames > 0.6:
                image = cv2.GaussianBlur(image, (5, 5), 0)
                self.final_image = np.asarray(image, dtype="uint8")
                print('Fingerprint image complete')
            else:
                print('Failed before reaching 60% completion.  Please retry with better quality movie.')

    def write_fingerprint_image(self):
        '''
        Writes MovieFingerprint image to file

        :return: void
        '''
        if self.final_image is not None:
            cv2.imwrite("images\{}.jpg".format(self.movie_title), self.final_image)  # save frame as JPEG file
            print('Fingerprint image written to images\{}.jpg'.format(self.movie_title))
        else:
            print('Error writing Fingerprint Image, make sure to get it first with make_fingerprint()')

    def get_matching_image(self):
        '''
        Compare MovieFingerprint image to regularly sampled movie frames to find the closest matching frame

        :return: void
        '''
        # Compare averaged image to a regularly sampled movie frames to find the closest match

        if self.final_image is None:
            new_image_path = input('Enter path of image to match to movie frame: ')
            self.final_image = cv2.imread(new_image_path)

        frame_count = 1
        video = cv2.VideoCapture(self.movie_path)
        final_image_width_quarter = int(self.image_width / 4.0)
        final_image_height_quarter = int(self.output_image_height / 4.0)
        final_image_small = cv2.resize(self.final_image, (final_image_width_quarter, final_image_height_quarter),
                                       interpolation=cv2.INTER_CUBIC)
        final_image_small_YCrCb = cv2.cvtColor(final_image_small, cv2.COLOR_BGR2YCrCb)  # Convert to YCrCb color space 

        success, best_match_image = video.read()
        best_match_image_score = math.inf

        while success and frame_count < self.fraction_of_movie_to_capture * self.total_frames:
            success, temp_image = video.read()
            if not success:
                print('FAILURE at image comparison, current frame is ', frame_count)
            if frame_count % self.sample_rate == 0:
                print('Comparison is {}% complete'.format(round(100 * frame_count / self.total_frames, 1)))
                temp_image_small = cv2.resize(temp_image, (final_image_width_quarter, final_image_height_quarter),
                                              interpolation=cv2.INTER_CUBIC)
                temp_image_small = cv2.GaussianBlur(temp_image_small, (5, 5), 0)
                temp_image_small_YCrCb = cv2.cvtColor(temp_image_small,
                                                      cv2.COLOR_BGR2YCrCb)  # Convert to YCrCb color space

                # Scoring function is modified RMS of difference between Y/Cr/Cb color channels of the averaged image found
                # with makeFingerprint() and each frame gathered by the video.read() call at the top of this method
                temp_image_score = math.sqrt(np.sum(
                    0.5 * np.square((final_image_small_YCrCb[:, :, 0] - temp_image_small_YCrCb[:, :, 0]))
                    + np.square((final_image_small_YCrCb[:, :, 1] - temp_image_small_YCrCb[:, :, 1]))
                    + np.square((final_image_small_YCrCb[:, :, 2] - temp_image_small_YCrCb[:, :, 2]))) / (
                                                 3 * (final_image_width_quarter * final_image_height_quarter)))

                if temp_image_score < best_match_image_score:
                    best_match_image_score = temp_image_score
                    best_match_image = temp_image
                frame_count += 1
            else:
                frame_count += 1

        print('best_match_image_score: ', best_match_image_score)
        self.best_match_image = best_match_image

    def write_matching_image(self):
        '''
        Writes matching image to file

        :return: void
        '''
        if self.best_match_image is not None:
            cv2.imwrite("images\{}_{}.jpg".format('MatchImage', self.movie_title),
                        self.best_match_image)  # save frame as JPEG file
            print('Matching image written to images\{}_{}.jpg'.format('MatchImage', self.movie_title))
        else:
            print('Error writing Match Image, make sure to get it first with get_matching_image()')

    def write_combined_image(self):
        '''
        Writes combined MovieFingerprint and matching image to file

        :return: void
        '''
        if self.final_image is not None and self.best_match_image is not None:
            scaled_image_width = 500
            scaled_image_height = int(scaled_image_width * float(self.output_image_height) / self.image_width)
            print(self.image_width)
            print(self.output_image_height)
            print(scaled_image_width)
            print(scaled_image_height)
            scaled_final_image = cv2.resize(self.final_image, (scaled_image_width, scaled_image_height),
                                            interpolation=cv2.INTER_CUBIC)
            scaled_best_match_image = cv2.resize(self.best_match_image, (scaled_image_width, scaled_image_height),
                                                 interpolation=cv2.INTER_CUBIC)
            middle_black_bar = np.zeros((scaled_final_image.shape[0], 10, scaled_final_image.shape[2]))

            cv2.imwrite("images\{}_{}.jpg".format('Both', self.movie_title),
                        np.concatenate((scaled_final_image, middle_black_bar, scaled_best_match_image),
                                       axis=1))  # save side-by-side image as JPEG file
        else:
            print(
            'Error writing Side-by-Side Image, make sure to get both images first with make_fingerprint() and get_matching_image()')
