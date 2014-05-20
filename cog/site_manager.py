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

       [esgf]
       ESGF_HOSTNAME=esg-datanode.jpl.nasa.gov
       ESGF_DBURL=postgresql://<db_username>:<db_password>@localhost/esgcet
       IDP_WHITELIST=/esg/config/esgf_idp_static.xml
       
       [peers]
       http|//localhost|8001
    '''

    # location of site specific settigs configuration file
    cog_config_dir = os.getenv('COG_CONFIG_DIR', '/usr/local/cog')
    CONFIGFILEPATH = os.path.join(cog_config_dir, 'cog_settings.cfg')

    def __init__(self):
        '''Initialization method reads the configuration file.'''

        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        configFilePath = os.path.expanduser(SiteManager.CONFIGFILEPATH)
        try:
            config = self.config.read( configFilePath )
            if not config:
                # if the configFilePath cannot be read (ie: doesn't exist), raise an error
                raise ValueError

        except Exception as e:
            print "Error reading site settings configuration file: %s" % configFilePath

    def get(self, name, section='default', default=None):
        '''Method that retrieves a settings value from a specified section of the configuration file.'''
        
        if self.config.has_option(section, name):
            return self.config.get(section, name)
        else:
            return default

    def hasConfig(self, section):
        '''Returns True if the configuration file contains the named section.'''

        return self.config.has_section(section)

    def getPeers(self):
        '''Returns a list of peer site URLs.
           Will replace the '|' with the ':' character for all URLs.
        '''
        
        peers = []
        if self.hasConfig('peers'):
            for option in self.config.options('peers'):
                # remove last '/'
                if option[-1]=='/':
                    option = option[0:-1]
                peers.append( option.replace('|',':') )
        return peers
    
siteManager = SiteManager()
            