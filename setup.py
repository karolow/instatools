from setuptools import setup, find_packages

setup(
    name='instagramtools',
    version='0.0.1',
    description='A Python package to facilitate acquisition and preprocessing of data from Instagram API',
    packages=find_packages(include=['instatools', 'instatools.*'])
)
