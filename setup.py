import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cog",
    version = "3.2.0",
    author = "CoG Development Team",
    author_email = "cog_support@list.woc.noaa.gov",
    description = ("Earth System CoG: web interface for the Earth System Grid Federation"),
    license = "BSD",
    keywords = "earth system cog grid federation",
    url = "https://github.com/EarthSystemCoG/COG",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=['django==1.8.3',
                      'django-grappelli==2.4.5',
                      'django-openid-auth==0.7', # must be installed independently from fork
                      'sqlalchemy==0.9.2',
                      'south==1.0.0',
                      'psycopg2==2.5.2',
                      'python-openid==2.2.5',
                      'passlib==1.6.2',
                      'pysqlite==2.6.3',        
                      'django-contrib-comments==1.6.1',   
                      'globusonline-transfer-api-client==0.10.16',   
                      "pillow==3.1.0", # must be installed with --use-wheel on MAC-OSX
                      'django-simple-captcha==0.4.5'
                      ],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2 :: Only",
        'Environment :: Web Environment',
        "Framework :: Django",
    ],
    #cmdclass={ 'install': CustomInstallCommand },
    entry_points = {
     "distutils.commands": [ "setup_cog = cog.installation.setup:CogSetupCommand"]
    },
    #dependency_links = ["http://effbot.org/downloads/"],
)
