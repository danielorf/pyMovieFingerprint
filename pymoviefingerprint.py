import cv2
import numpy as np
import math
import sys


class MovieFingerprint(object):

    def __init__(self, movie_path, movie_title):
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

    def setPath(self, movie_path):
        self.movie_path = movie_path

    def setTitle(self, movie_title):
        self.movie_title = movie_title

    def makeFingerprint(self):
        if (self.movie_path or self.movie_title) is not None:
            print(self.movie_title)
            # video = cv2.VideoCapture(self.movie_path)
            # self.total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            # sample_rate = int(round(self.total_frames / self.total_samples, 0))

            print('Total frames: ', self.total_frames)
            print('Frames to capture: ', self.fraction_of_movie_to_capture * self.total_frames)
            print('Sample rate: ', self.sample_rate)
            print()

            sampled_frames = float(self.total_frames) / self.sample_rate
            # success, temp_image = self.video.read()
            # self.image_width = int(temp_image.shape[1] * float(self.output_image_height) / temp_image.shape[0])

            temp_image_rescaled = cv2.resize(self.temp_image, (self.image_width, self.output_image_height), interpolation=cv2.INTER_CUBIC)
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
                    temp_image_rescaled[:, :, 1] = cv2.equalizeHist(temp_image_rescaled[:, :, 1])
                    temp_image_rescaled[:, :, 2] = cv2.equalizeHist(temp_image_rescaled[:, :, 2])
                    temp_image_rescaled = cv2.cvtColor(temp_image_rescaled, cv2.COLOR_HSV2BGR)
                    temp_image_rescaled = cv2.GaussianBlur(temp_image_rescaled, (5, 5), 0)
                    temp_image_rescaled = cv2.resize(temp_image_rescaled, (self.image_width, self.output_image_height),
                                            interpolation=cv2.INTER_CUBIC)
                    image += np.asarray(temp_image_rescaled, dtype="int32") / sampled_frames
                    frame_count += 1
                else:
                    frame_count += 1

            # find_matching_image_flag = False
            if frame_count / self.total_frames > 0.6:
                # find_matching_image_flag = True
                image = cv2.GaussianBlur(image, (5, 5), 0)
                self.final_image = np.asarray(image, dtype="uint8")

                # cv2.imshow(' ', image)
                cv2.imwrite("{}.jpg".format(self.movie_title), self.final_image)  # save frame as JPEG file
            else:
                print('Failed before reaching 60% completion.  Please retry with better quality movie.')

                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

    def getMatchingImage(self):
        #  Compare averaged image to a bunch of movie frames to find the closest match

        if self.final_image is None:
            new_image_path = input('Enter path of image to match to movie frame: ')
            self.final_image = cv2.imread(new_image_path)

        frame_count = 1
        success = True
        video = cv2.VideoCapture(self.movie_path)
        final_image_width_quarter = int(self.image_width / 4.0)
        final_image_height_quarter = int(self.output_image_height / 4.0)
        final_image_small = cv2.resize(self.final_image, (final_image_width_quarter, final_image_height_quarter),
                                       interpolation=cv2.INTER_CUBIC)
        final_image_small_HSV = cv2.cvtColor(final_image_small, cv2.COLOR_BGR2HSV)
        final_image_small_YCrCb = cv2.cvtColor(final_image_small, cv2.COLOR_BGR2YCrCb)

        success, best_match_image = video.read()
        # best_match_image_small = cv2.resize(best_match_image,(final_image_width_quarter,final_image_height_quarter), interpolation=cv2.INTER_CUBIC)
        # best_match_image_score = math.sqrt(np.sum(final_image_small-best_match_image_small)**2)
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
                temp_image_small_HSV = cv2.cvtColor(temp_image_small, cv2.COLOR_BGR2HSV)
                temp_image_small_YCrCb = cv2.cvtColor(temp_image_small, cv2.COLOR_BGR2YCrCb)

                # temp_image_score = math.sqrt(
                #     0.5 * np.sum(final_image_small_HSV[:, :, 0] - temp_image_small_HSV[:, :, 0]) ** 2 +
                #     np.sum(final_image_small_HSV[:, :, 1] - temp_image_small_HSV[:, :, 1]) ** 2 +
                #     0.5 * np.sum(final_image_small_HSV[:, :, 2] - temp_image_small_HSV[:, :, 2]) ** 2)

                # temp_image_score = math.sqrt(
                #     np.sum(final_image_small_YCrCb[:, :, 0] - temp_image_small_YCrCb[:, :, 0]) ** 1.5
                #     + np.sum(final_image_small_YCrCb[:, :, 1] - temp_image_small_YCrCb[:, :, 1]) ** 2
                #     + np.sum(final_image_small_YCrCb[:, :, 2] - temp_image_small_YCrCb[:, :, 2]) ** 2)

                temp_image_score = math.sqrt(np.sum(
                    0.5 * np.square((final_image_small_YCrCb[:, :, 0] - temp_image_small_YCrCb[:, :, 0]))
                    + np.square((final_image_small_YCrCb[:, :, 1] - temp_image_small_YCrCb[:, :, 1]))
                    + np.square((final_image_small_YCrCb[:, :, 2] - temp_image_small_YCrCb[:, :, 2]))) / (
                                                 3 * (final_image_width_quarter * final_image_height_quarter)))

                if temp_image_score < best_match_image_score:
                    best_match_image_score = temp_image_score
                    best_match_image = temp_image
                    best_match_image_small = cv2.resize(best_match_image,
                                                        (final_image_width_quarter, final_image_height_quarter),
                                                        interpolation=cv2.INTER_CUBIC)
                frame_count += 1
            else:
                frame_count += 1

        print('best_match_image_score: ', best_match_image_score)
        cv2.imwrite("{}_{}.jpg".format('MatchImage', self.movie_title), best_match_image)  # save frame as JPEG file