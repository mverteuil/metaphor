from __future__ import print_function

from collections import deque
from datetime import timedelta
from glob import glob
from itertools import chain
from itertools import groupby
import os
import time

from PIL import Image
from dateutil import parser as dateparser
import imageio
import ssim


class CompareImageSimilarityAndModifiedDate(object):
    __slots__ = ['image', 'similarity']

    def __init__(self, image):
        self.image = image

    def __eq__(self, other):
        reasonable_match = self.similar_image(other) or self.similar_modified_date(other)
        if reasonable_match:
            self.image = other.image
        return reasonable_match

    def similar_image(self, other):
        self.similarity = ssim.compute_ssim(Image.open(self.image), Image.open(other.image))
        return self.similarity > 0.55

    def similar_modified_date(self, other):
        current_modified_epoch = os.path.getmtime(self.image)
        current_modified = dateparser.parse(time.ctime(current_modified_epoch))

        next_modified_epoch = os.path.getmtime(other.image)
        next_modified = dateparser.parse(time.ctime(next_modified_epoch))

        time_interval = next_modified - current_modified
        return self.similarity < 0.5 and time_interval < timedelta(seconds=30)


class Metaphor(object):
    def __init__(self, image_path):
        self.image_path = image_path

    def get_images(self):
        for suffix in ('gif', 'png', 'jpg', 'tif', 'bmp', ):
            for image_file in glob(os.path.join(self.image_path, '*.{suffix}'.format(suffix=suffix))):
                yield image_file

    def get_sequences(self):
        for _, group in groupby(self.get_images(), key=CompareImageSimilarityAndModifiedDate):
            yield list(group)

    def run(self):
        for sequence_id, sequence in enumerate(self.get_sequences()):
            sequence_filename = 'sequence_{sequence_id}.gif'.format(**locals())
            image_sequence = [imageio.imread(frame) for frame in sequence]
            imageio.mimwrite(sequence_filename, image_sequence, format='GIF', loop=0, duration=1.5)
            print(sequence_filename, ' saved')
