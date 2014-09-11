'''
Script to fix teh ESGF database at NOAA.

@author: cinquini
'''

import os
import sys
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.plugins.esgf.security import ESGFDatabaseManager

esgfDatabaseManager = ESGFDatabaseManager()

esgfDatabaseManager.listUsers()