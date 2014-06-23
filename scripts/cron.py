#!/usr/bin/python

'''
Script to execute django recurrent tasks through cron.

Run as: python cron.py

'''
import os, sys
import datetime
import logging

parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)

# load CoG settings
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'



# sync projects from remote sites
from cog.project_manager import projectManager
sites = projectManager.sync()
logging.debug('Cron syncProjects: time=%s synchronized projects from sites=%s' % (datetime.datetime.now(), sites))