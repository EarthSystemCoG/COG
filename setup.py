import os
import logging
from setuptools import setup, find_packages
from cog.installation.setup import CogSetupCommand

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

rel = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)
logging.basicConfig(
    filename=rel('setup.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(name)s: %(message)s',
)

setup(
    name = "cog",
    version = "3.11",
    author = "CoG Development Team",
    author_email = "cog_support@list.woc.noaa.gov",
    description = ("Earth System CoG: web interface for the Earth System Grid Federation"),
    license = "BSD",
    keywords = "earth system cog grid federation",
    url = "https://github.com/EarthSystemCoG/COG",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2 :: Only",
        'Environment :: Web Environment',
        "Framework :: Django",
    ],
    cmdclass={ 'setup_cog': CogSetupCommand },
    #entry_points = {
    # "distutils.commands": [ "setup_cog = cog.installation.setup:CogSetupCommand"]
    #},
)
