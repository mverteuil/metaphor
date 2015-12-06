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
    print(similarity)
    return similarity


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    image_files = glob(os.path.join(here, '..', 'test_images', '*.png'))

    diff_history = deque([])
    similarity_history = deque([])
    for current_image, preview_image in preview_list(image_files):
        diff_history.append(compare_preview_image_modified(current_image, preview_image))
        similarity_history.append(compare_preview_image_similarity(current_image, preview_image))
        for current_diff, preview_diff in preview_list(diff_history):
            if current_diff < preview_diff:
                print('curr: {}'.format(current_diff))
            else:
                print('prev: {}'.format(preview_diff))

        for current_similarity, preview_similarity in preview_list(similarity_history):
            if current_similarity < preview_similarity:
                print('curr: {}'.format(current_similarity))
            else:
                print('prev: {}'.format(preview_similarity))

        print('-'*80, end='\n\n')
