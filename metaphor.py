from datetime import timedelta
from glob import glob
from itertools import groupby
import os
import time

from PIL import Image
from dateutil import parser as dateparser
import click
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
    def __init__(self, source_path, target_path):
        self.source_path = source_path
        self.target_path = target_path

    def _create_target_path(self):
        try:
            os.makedirs(self.target_path)
            click.echo('Target created.')
        except os.error:
            click.echo('Target already exists.')

    def get_images(self):
        for suffix in ('gif', 'png', 'jpg', 'tif', 'bmp', ):
            for image_file in glob(os.path.join(self.source_path, '*.{suffix}'.format(suffix=suffix))):
                yield image_file

    def get_sequences(self):
        images = self.get_images()
        for _, group in groupby(images, key=CompareImageSimilarityAndModifiedDate):
            yield list(group)

    def run(self):
        self._create_target_path()
        sequences = self.get_sequences()
        for sequence_id, sequence in enumerate(sequences):
            sequence_filename = 'sequence_{sequence_id}.gif'.format(**locals())
            target_filename = os.path.join(self.target_path, sequence_filename)
            image_sequence = [imageio.imread(frame) for frame in sequence]
            os.makedirs
            imageio.mimwrite(target_filename, image_sequence, format='GIF', loop=0, duration=0.5)
            click.echo(target_filename + ' saved')


class Cutter(object):
    def __init__(self, source_path, target_path, left, top, right, bottom):
        self.source_path = source_path
        self.target_path = target_path
        self.box = (left, top, right, bottom)

    def _create_target_path(self):
        try:
            os.makedirs(self.target_path)
            click.echo('Target created.')
        except os.error:
            click.echo('Target already exists.')

    def get_images(self):
        for suffix in ('gif', 'png', 'jpg', 'tif', 'bmp', ):
            for image_file in glob(os.path.join(self.source_path, '*.{suffix}'.format(suffix=suffix))):
                yield image_file

    def run(self):
       self._create_target_path()
       images = self.get_images()
       for index, image in enumerate(images):
           with Image.open(image) as img:
               new_image = img.crop(self.box)
               new_image_name = '{index}.png'.format(index=index)
               new_image_path = os.path.join(self.target_path, new_image_name)
               new_image.save(new_image_path, format='PNG')


@click.command()
@click.option('--source-path', default='test_images', type=click.Path(exists=True, file_okay=False))
@click.option('--target-path', default='output', type=click.Path(exists=False, file_okay=False))
def cli(source_path, target_path):
    metaphor = Metaphor(source_path, target_path)
    metaphor.run()


@click.command()
@click.option('--source-path', default='test_images', type=click.Path(exists=True, file_okay=False))
@click.option('--target-path', default='output', type=click.Path(exists=False, file_okay=False))
@click.option('--left', default=0, type=int)
@click.option('--top', default=0, type=int)
@click.option('--right', default=0, type=int)
@click.option('--bottom', default=0, type=int)
def cutter(source_path, target_path, left, top, right, bottom):
    cutter = Cutter(source_path, target_path, left, top, right, bottom)
    cutter.run()
