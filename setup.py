import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cog",
    version = "2.11.0",
    author = "CoG Development Team",
    author_email = "cog_support@list.woc.noaa.gov",
    description = ("Earth System CoG: web interface for the Earth System Grid Federation"),
    license = "BSD",
    keywords = "earth system cog grid federation",
    url = "https://github.com/EarthSystemCoG/COG",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=['pil==1.1.7',
                      'django==1.6.5',
                      'django-grappelli==2.4.5',
                      'django-openid-auth==0.5',
                      'django-pagination==1.0.7',
                      'sqlalchemy==0.9.2',
                      'south==1.0.0',
                      'psycopg2==2.5.2',
                      'python-openid==2.2.5',
                      'passlib==1.6.2',
                      'pysqlite==2.6.3',        
                      'django-contrib-comments==1.5',          
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
    }

)
