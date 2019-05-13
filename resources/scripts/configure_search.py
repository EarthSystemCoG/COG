# Python script to configure off-band a project advanced search
import sys, os, ConfigParser

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.config.search import read_config
#from django.conf import settings

print('Upgrading COG')

# read search configurations
configs = { 'StandardDistribution': 'cog/config/search/standard_distribution.cfg',
            #'NCPP': 'cog/config/search/ncpp.cfg',
            #'Downscaling-2013': 'cog/config/search/ncpp.cfg',
          }

for key in configs:
    read_config(key, configs[key])
