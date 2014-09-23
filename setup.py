import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cog",
    version = "2.7.0",
    author = "CoG Development Team",
    author_email = "cog_support@list.woc.noaa.gov",
    description = ("Earth System CoG: web interface for the Earth System Grid Federation"),
    license = "BSD",
    keywords = "earth system cog grid federation",
    url = "https://github.com/EarthSystemCoG/COG",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=['pil'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2 :: Only",
        'Environment :: Web Environment',
        "Framework :: Django",
    ],
)
