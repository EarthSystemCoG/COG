import os
import ConfigParser 

class SiteManager(object):
    '''Class used to load site-specific settings at COG startup.
    
       Example configuration file:
       [default]
       SITE_ID=1
       TIME_ZONE=America/Denver
       COG_MAILING_LIST=cog_info@list.woc.noaa.gov
       SECRET_KEY=yb@$-bub$i_mrxqe5it)v%p=^(f-h&x3%uy040x))19g^iha&#
       DATABASE_USER=database_user
       DATABASE_PORT=database_port
       DATABASE_PORT=5432
       
    '''
    
    # location of site specific settigs configuration file
    cog_config_dir = os.getenv('COG_CONFIG_DIR', '/usr/local/cog')
    CONFIGFILEPATH = os.path.join(cog_config_dir, 'cog_settings.cfg')

    # dictionary containing default values for all site settings
    DEFAULTS = {
                'SITE_ID': 1,
                'TIME_ZONE': 'America/Denver',
                'COG_MAILING_LIST': 'cog_info@list.woc.noaa.gov',
                'SECRET_KEY': 'no default',
                'DATABASE_USER':'no default',
                'DATABASE_PASSWORD':'no default',
                'DATABASE_PORT':'5432',
               }
    
    def __init__(self):
        '''Initialization method reads the configuration file.'''

        self.config = ConfigParser.RawConfigParser(SiteManager.DEFAULTS)
        configFilePath = os.path.expanduser(SiteManager.CONFIGFILEPATH)
        try:
            config = self.config.read( configFilePath )
            if not config:
                # if the configFilePath cannot be read (ie: doesn't exist), raise an error
                raise ValueError
            
        except Exception as e:
            print "Error reading site settings configuration file: %s" % configFilePath
        
    def get(self, name):
        '''Method that retrieves a settings value from the 'default' section of the configuration file.'''
        return self.config.get('default', name)
        