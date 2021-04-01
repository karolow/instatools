from setuptools import setup, find_packages

setup(
    name='instagramtools',
    version='0.0.1',
    description='A collection of tools to facilitate acquisition and analysis of data from the Instagram API',
    packages=find_packages(include=['instatools', 'instatools.*'])
)
