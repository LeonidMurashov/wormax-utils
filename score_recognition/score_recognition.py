import keras
import cv2
import numpy as np
from joblib import load

score_rect = [894, 208, 948, 222]
digits_classifier = keras.models.load_model('SVHN_classifier.hdf5')
empty_digit_classifier = load('empty_digit_classifier.joblib') 


def crop_score(frame):
	return frame[score_rect[1]:score_rect[3], 
				 score_rect[0]:score_rect[2]]


def get_digit_frames(number_frame):
    digit_frames = []
    for i in range(6):
        framed = number_frame[:, number_frame.shape[1] * i // 6:
                                 number_frame.shape[1] * (i + 1) // 6]
        framed = cv2.resize(framed, dsize=(32, 32), interpolation=cv2.INTER_CUBIC)
        framed = np.clip(framed, 0, 1)
        digit_frames.append(framed)
    return np.array(digit_frames)


def get_score_from_crop(img):
	digit_frames = get_digit_frames(img)
	empty_digit_criterion = digit_frames.mean(axis=(1, 2, 3)) > 0.15
	empty_estimate = empty_digit_classifier.predict(digit_frames.reshape(-1, 32 * 32 * 3))
	digits = np.argmax(digits_classifier.predict(digit_frames), axis=-1)
	digits = digits * empty_digit_criterion * empty_estimate
	return sum(digit * 10**i for i, digit in enumerate(digits[::-1]))


def get_score(frame):
	img = crop_score(frame)
	return get_score_from_crop(img)