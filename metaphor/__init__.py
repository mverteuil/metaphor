from __future__ import print_function

from collections import deque
from glob import glob
import itertools
import os
import time

from dateutil import parser as dateparser
from PIL import Image
import imagehash
import ssim


def preview_list(iterable):
    """ Creates a new iterable that includes a preview of the next item as iteration occurs. """
    # Fork the iterable
    original, preview = itertools.tee(iterable)
    # Advance the preview iterable to be one ahead of the original
    next(preview)
    return zip(original, preview)


def compare_preview_image_modified(current_image, preview_image):
    current_modified_epoch = os.path.getmtime(current_image)
    current_modified = dateparser.parse(time.ctime(current_modified_epoch))

    if preview_image:
        next_modified_epoch = os.path.getmtime(preview_image)
        next_modified = dateparser.parse(time.ctime(next_modified_epoch))
        diff = next_modified - current_modified
    else:
        next_modified = None
        diff = None

    print(current_modified)
    return diff



def compare_preview_image_hash(current_image, preview_image, hash_function=imagehash.average_hash):
    current = hash_function(Image.open(current_image))
    preview = hash_function(Image.open(preview_image))
    print(current, preview)


def compare_preview_image_similarity(current_image, preview_image):
    similarity = ssim.compute_ssim(Image.open(current_image), Image.open(preview_image))
    return similarity


class AdjacentKey(object):
    __slots__ = ['obj']
    def __init__(self, obj):
        self.obj = obj
    def __eq__(self, other):
        similarity = compare_preview_image_similarity(self.obj, other.obj)
        reasonable_match = similarity > 0.55
        if reasonable_match:
            self.obj = other.obj
        return reasonable_match


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    image_files = glob(os.path.join(here, '..', 'test_images', '*.png'))
    groups = [list(g) for k, g in itertools.groupby(image_files, key=AdjacentKey)]
    print(groups)
