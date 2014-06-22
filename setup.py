from setuptools import setup, find_packages

requirements = [
    # Requests 1.2.1-1.2.3 - won't install under Python 3.3
    'requests==1.2.0',
    'feedparser',
    'cython==0.19.1',
    'pytaglib==0.3.5',
]

setup(
    name='podyogi',
    version='0.0.1',
    packages=[''],
    url='https://bitbucket.org/poirier/pypodder/',
    license='Apache 2.0',
    author='Dan Poirier',
    author_email='dan@poirier.us',
    description='Podcatcher for Pythonistas',
    install_requires=requirements,
    long_description=open("README.rst").read(),
)
