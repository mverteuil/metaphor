import os

from . import Metaphor

here = os.path.dirname(__file__)
image_path = os.path.join(here, '..', 'test_images')
metaphor = Metaphor(image_path)
metaphor.run()
