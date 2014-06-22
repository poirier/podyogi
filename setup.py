from setuptools import setup, find_packages

requirements = [
    'cython==0.19.1',
    'pytaglib==0.3.5',
    'requests==2.3.0',
    'feedparser==5.1.3'
]

setup(
    name='podyogi',
    version='0.0.1',
    packages=[''],
    url='https://bitbucket.org/poirier/podyogi/',
    license='Apache 2.0',
    author='Dan Poirier',
    author_email='dan@poirier.us',
    description='Podcatcher for Pythonistas',
    install_requires=requirements,
    long_description=open("README.rst").read(),
)
