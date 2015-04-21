#!/bin/sh

#==== SITE SPECIFIC PARAMETERS - CHANGE AS NEEDED =====

# CoG software root directory
export COG_DIR=/usr/local/cog

# true if CoG is installed on ESGF node
export ESGF=true

# the user and group running the CoG application
export USER=apache
export GROUP=apache

# the specific CoG branch OR version to install
#export COG_TAG=master
export COG_TAG=v2.12.0

# the Python installation from which to create the venev
export PATH=/usr/local/uvcdat/bin:$PATH

#=== ESGF INSTALLATION LOGIC - DO NOT CHANGE =========

# ESGF version
export VERSION=$COG_TAG

# ESGF installation path
export INSTALLPATH=$COG_DIR/cog_install

# ESGF common installation script
export INSTALLARG_SCRIPT=$INSTALLPATH/resources/scripts/installarg.sh
if [ -e "$INSTALLARG_SCRIPT" ]; then
  source $INSTALLARG_SCRIPT
fi

#=== CoG INSTALLATION LOGIC - DO NOT CHANGE ==========

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
cd $COG_DIR
rm -rf venv/lib/python2.7/site-packages/cog*

# change ownership of COG_CONFIG_DIR/site_media
chown -R $USER:$GROUP $COG_CONFIG_DIR
chown -R $USER:$GROUP $COG_INSTALL_DIR
