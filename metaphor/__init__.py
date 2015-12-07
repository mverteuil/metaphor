from __future__ import print_function

from collections import deque
from datetime import timedelta
from glob import glob
from pprint import pprint
import itertools
import os
import time

from PIL import Image
from dateutil import parser as dateparser
import imageio
import ssim


def compare_preview_image_modified(current_image, preview_image):
    current_modified_epoch = os.path.getmtime(current_image)
    current_modified = dateparser.parse(time.ctime(current_modified_epoch))

    next_modified_epoch = os.path.getmtime(preview_image)
    next_modified = dateparser.parse(time.ctime(next_modified_epoch))
    diff = next_modified - current_modified
    return diff


def compare_preview_image_similarity(current_image, preview_image):
    similarity = ssim.compute_ssim(Image.open(current_image), Image.open(preview_image))
    return similarity


class AdjacentKey(object):
    __slots__ = ['obj']

    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        similarity = compare_preview_image_similarity(self.obj, other.obj)
        time_interval = compare_preview_image_modified(self.obj, other.obj)
        reasonable_match = similarity > 0.55 or (similarity < 0.5 and time_interval < timedelta(seconds=30))

        #print(self.obj, other.obj, reasonable_match, similarity, time_interval)

        if reasonable_match:
            self.obj = other.obj
        return reasonable_match


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    image_files = glob(os.path.join(here, '..', 'test_images', '*.png'))
    sequences = [list(g) for k, g in itertools.groupby(image_files, key=AdjacentKey)]
    for sequence_id, sequence in enumerate(sequences):
        sequence_filename = 'sequence_{sequence_id}.gif'.format(**locals())
        image_sequence = [imageio.imread(frame) for frame in sequence]
        imageio.mimwrite(sequence_filename, image_sequence, format='GIF', loop=0, duration=1.5)
        print(sequence_filename, ' saved')
