from setuptools import setup

setup(
    name='metaphor',
    version='0.1',
    py_modules=['metaphor'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        metaphor=metaphor:cli
    ''',
)
