# Python script to configure off-band a project advanced search
import sys, os, ConfigParser

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.config.search import config_project_search
#from django.conf import settings

print 'Upgrading COG'

# read search configurations
configs = { 'NCPP': 'cog/config/search/ncpp.cfg',
            'Downscaling-2013': 'cog/config/search/ncpp.cfg' }

for key in configs:
    config_project_search(key, configs[key])
