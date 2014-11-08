#!/bin/sh

# pre-requisites
pip install virtualenv

# define directory structure
#export COG_DIR=/usr/local/cog
export COG_DIR=/Users/cinquini/tmp/cog
mkdir -p $COG_DIR

export COG_CONFIG_DIR=$COG_DIR/cog_config
mkdir -p $COG_CONFIG_DIR

export COG_INSTALL_DIR=$COG_DIR/cog_install
# note: the above directory will be created at initial checkout

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
git checkout v2.7.0

# install CoG dependencies within Python virtual environment
cd $COG_INSTALL_DIR
python setup.py install

# create or upgrade CoG installation
python setup.py setup_cog --esgf=true

# cleanup CoG egg
cd $COG_INSTALL_DIR
rm -rf venv/lib/python2.7/site-packages/cog*
