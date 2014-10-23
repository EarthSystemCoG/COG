#!/bin/sh

# script to update the state of CoG projects around the federation

# reference the proper python installation
export PATH=/usr/local/bin:$PATH

# reference the COG installation
export COG_INSTALL_DIR=/usr/local/cog/cog_install

# reference the COG configuration
export COG_CONFIG_DIR=/usr/local/cog/cog_config

python $COG_INSTALL_DIR/manage.py sync_projects
