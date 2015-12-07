from setuptools import setup

setup(
    name='metaphor',
    version='0.1',
    py_modules=['metaphor'],
    install_requires=[
        'Click',
        'Pillow',
        'imageio',
        'pyssim',
        'python-dateutil',
    ],
    entry_points='''
        [console_scripts]
        cutter=metaphor:cutter
        metaphor=metaphor:cli
    ''',
)
