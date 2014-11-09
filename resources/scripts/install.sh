#!/bin/sh

# CoG software root directory
export COG_DIR=/usr/local/cog

# true if CoG is installed on ESGF node
export ESGF=true

# the specific CoG tag to install
export COG_TAG=v2.7.1

# the user and group running the CoG application
export USER=tomcat
export GROUP=tomcat

#===========================================

# pre-requisites
pip install virtualenv

# root directory for installation
mkdir -p $COG_DIR

# directory for local settings
export COG_CONFIG_DIR=$COG_DIR/cog_config
mkdir -p $COG_CONFIG_DIR

# installation directory
# will be created during git checkout
export COG_INSTALL_DIR=$COG_DIR/cog_install

# use Python virtual environment
cd $COG_DIR
virtualenv venv
source venv/bin/activate
echo 'Using Python:' `which python`

# initial checkout CoG software stack
cd $COG_DIR
if [ ! -d "$COG_INSTALL_DIR" ]; then
  git clone https://github.com/EarthSystemCoG/COG cog_install
fi

# checkout a specific tag or version
cd $COG_INSTALL_DIR
git pull
git checkout $COG_TAG

# install CoG dependencies within Python virtual environment
cd $COG_INSTALL_DIR
python setup.py install

# create or upgrade CoG installation
python setup.py setup_cog --esgf=$ESGF

# cleanup CoG egg
cd $COG_INSTALL_DIR
rm -rf venv/lib/python2.7/site-packages/cog*

# change ownership of site_media
chown -R $USER:$GROUP $COG_CONFIG_DIR
