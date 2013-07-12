from distutils.core import setup

setup(
    name='pypodder',
    version='0.0.1',
    packages=[''],
    url='https://bitbucket.org/poirier/pypodder/',
    license='Apache 2.0',
    author='poirier',
    author_email='dan@poirier.us',
    description='Podcatcher',
    requires=['requests', 'feedparser']
)
FIXME require recent enough 'requests'