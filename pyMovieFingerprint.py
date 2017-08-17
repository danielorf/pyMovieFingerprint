import cv2
import numpy as np

total_samples = 500
output_image_height = 1080
fraction_of_movie_to_capture = 0.9  # Used to cut out credits frames which are often black

movie_path = r''
movie_title = movie_path.split('\\')[-1].split('.')[0]
print(movie_title)
video = cv2.VideoCapture(movie_path)
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
sample_rate = int(round(total_frames / total_samples, 0))

print('Total frames: ', total_frames)
print('Frames to capture: ', fraction_of_movie_to_capture * total_frames)
print('Sample rate: ', sample_rate)
print()

sampled_frames = float(total_frames) / sample_rate
success, temp_image = video.read()
image_width = int(temp_image.shape[1] * float(output_image_height) / temp_image.shape[0])

temp_image = cv2.resize(temp_image, (image_width, output_image_height), interpolation=cv2.INTER_CUBIC)
image = np.asarray(temp_image, dtype="int32") / sampled_frames

frame_count = 1
success = True

while success and frame_count < fraction_of_movie_to_capture * total_frames:
    success, temp_image = video.read()
    if not success:
        print('FAILURE, current frame is ', frame_count)
    if frame_count % sample_rate == 0:
        print('{}% complete'.format(round(100 * frame_count / total_frames, 1)))

        print('frame_count: ', frame_count)

        temp_image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2HSV)
        temp_image[:, :, 1] = cv2.equalizeHist(temp_image[:, :, 1])
        temp_image[:, :, 2] = cv2.equalizeHist(temp_image[:, :, 2])
        temp_image = cv2.cvtColor(temp_image, cv2.COLOR_HSV2BGR)
        temp_image = cv2.GaussianBlur(temp_image, (5, 5), 0)
        temp_image = cv2.resize(temp_image, (image_width, output_image_height), interpolation=cv2.INTER_CUBIC)
        image += np.asarray(temp_image, dtype="int32") / sampled_frames
        frame_count += 1
    else:
        frame_count += 1

if frame_count / total_frames > 0.6:
    image = cv2.GaussianBlur(image, (5, 5), 0)
    image = np.asarray(image, dtype="uint8")

    # cv2.imshow(' ', image)
    cv2.imwrite("{}.jpg".format(movie_title), image)  # save frame as JPEG file
else:
    print('Failed before reaching 60% completion.  Please retry with better quality movie.')

cv2.waitKey(0)
cv2.destroyAllWindows()
