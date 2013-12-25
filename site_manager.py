import os
import ConfigParser 

class SiteManager(object):
    '''Class uses to load site-specific settings at COG startup.
    
       Example configuration file:
       [default]
       SITE_ID=1
       TIME_ZONE=America/Denver
       COG_MAILING_LIST=cog_info@list.woc.noaa.gov
       SECRET_KEY=yb@$-bub$i_mrxqe5it)v%p=^(f-h&x3%uy040x))19g^iha&#
       
    '''
    
    # location of site specific settigs configuration file
    CONFIGFILEPATH = '~/.cog_settings.cfg'

    # dictionary containing default values for all site settings
    DEFAULTS = {
                'SITE_ID': 1,
                'TIME_ZONE': 'America/Denver',
                'COG_MAILING_LIST': 'cog_info@list.woc.noaa.gov',
                'SECRET_KEY': 'yb@$-bub$i_mrxqe5it)v%p=^(f-h&x3%uy040x))19g^iha&#',
               }
    
    def __init__(self):
        '''Initialization methd reads the configuration file.'''
        
        self.config = ConfigParser.RawConfigParser(SiteManager.DEFAULTS)
        configFilePath = os.path.expanduser(SiteManager.CONFIGFILEPATH)
        try:
            self.config.read( configFilePath )
        except Exception as e:
            print "Error reading site settings configuration file: %s" % configFilePath
        
    def get(self, name):
        '''Method that retrieves a settings value from the 'default' section of the configuration file.'''
        return self.config.get('default', name)
        