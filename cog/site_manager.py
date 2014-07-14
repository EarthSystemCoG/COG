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
       DATABASE_NAME=cogdb
       DATABASE_USER=database_user
       DATABASE_PORT=database_port
       DATABASE_PORT=5432
       MY_PROJECTS_REFRESH_SECONDS=10

       [esgf]
       ESGF_HOSTNAME=esg-datanode.jpl.nasa.gov
       ESGF_DBURL=postgresql://<db_username>:<db_password>@localhost/esgcet
       IDP_WHITELIST=/esg/config/esgf_idp_static.xml
    '''
    
    # location of site specific settigs configuration file
    COG_CONFIG_DIR = os.getenv('COG_CONFIG_DIR', '/usr/local/cog')
    CONFIGFILEPATH = os.path.join(COG_CONFIG_DIR, 'cog_settings.cfg')

    def __init__(self):
        '''Initialization method reads the configuration file.'''

        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        # location of site specific settigs configuration file
        self.cog_config_dir = SiteManager.COG_CONFIG_DIR
        try:
            config = self.config.read( SiteManager.CONFIGFILEPATH )
            if not config:
                # if the configFilePath cannot be read (ie: doesn't exist), raise an error
                raise ValueError

        except Exception as e:
            print "Error reading site settings configuration file: %s" % SiteManager.CONFIGFILEPATH

    def get(self, name, section='default', default=None):
        '''Method that retrieves a settings value from a specified section of the configuration file.'''
        
        if self.config.has_option(section, name):
            return self.config.get(section, name)
        else:
            return default

    def hasConfig(self, section):
        '''Returns True if the configuration file contains the named section.'''

        return self.config.has_section(section)
    
siteManager = SiteManager()
            