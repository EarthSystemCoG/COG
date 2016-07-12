import os
import ConfigParser
import logging

from cog.constants import (SECTION_ESGF, SECTION_GLOBUS)

class SiteManager(object):
    '''Class used to load site-specific settings at COG startup.

       Example configuration file:

       [default]
       SITE_NAME=My Site
       SITE_DOMAIN=localhost:8000
       TIME_ZONE=America/Denver
       COG_MAILING_LIST=cog_info@list.woc.noaa.gov
       SECRET_KEY=yb@$-bub$i_mrxqe5it)v%p=^(f-h&x3%uy040x))19g^iha&#
       DATABASE_NAME=cogdb
       DATABASE_USER=database_user
       DATABASE_HOST=localhost
       DATABASE_PORT=5432
       MY_PROJECTS_REFRESH_SECONDS=3600
       # optional number of days after which password expire
       PASSWORD_EXPIRATION_DAYS=0
       # optional top-level URL to redirect user registration (no trailing '/')
       IDP_REDIRECT=https://www.earthsystemcog.org
       # whitelist of trusted Identity Providers
       IDP_WHITELIST=/esg/config/esgf_idp.xml, /esg/config/esgf_idp_static.xml
       # dev/prod server switch
       PRODUCTION_SERVER = True
       USE_CAPTCHA = True

       [ESGF]
       ESGF_HOSTNAME=esg-datanode.jpl.nasa.gov
       ESGF_DBURL=postgresql://<db_username>:<db_password>@localhost/esgcet
       ESGF_VERSION=v2.0-RC4.3-devel
       
       [EMAIL]
       EMAIL_SERVER=smtp.gmail.com
       # leave port blank if default
       EMAIL_PORT=
       EMAIL_SENDER=Earth System COG
       EMAIL_USERNAME=........
       EMAIL_PASSWORD=........
       EMAIL_SECURITY=STARTTLS
       
       [GLOBUS]
       PORTAL_GO_USERNAME = ..........
       PORTAL_GO_PASSWORD = ..........
       ENDPOINTS = /esg/config/esgf_endpoints.xml

    '''
    
    # location of site specific settigs configuration file
    COG_CONFIG_DIR = os.getenv('COG_CONFIG_DIR', '/usr/local/cog/cog_config')
    CONFIGFILEPATH = os.path.join(COG_CONFIG_DIR, 'cog_settings.cfg')

    def __init__(self):
        '''Initialization method reads the configuration file.'''

        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        # location of site specific settigs configuration file
        self.cog_config_dir = SiteManager.COG_CONFIG_DIR
        try:
            config = self.config.read( SiteManager.CONFIGFILEPATH )
            logging.info("Site manager: using CoG settings from file(s): %s" % config)
            if not config:
                # if the configFilePath cannot be read (ie: doesn't exist), raise an error
                raise ValueError

            print 'Initialized CoG settings from file: %s' % SiteManager.CONFIGFILEPATH
        except Exception as e:
            print "Error reading site settings configuration file: %s" % SiteManager.CONFIGFILEPATH

    def get(self, name, section='DEFAULT', default=None):
        '''Method that retrieves a settings value from a specified section of the configuration file.'''
        
        if self.config.has_option(section, name):
            return self.config.get(section, name)
        else:
            return default

    def hasConfig(self, section):
        '''Returns True if the configuration file contains the named section.'''

        return self.config.has_section(section)
    
    def isEsgfEnabled(self):
        '''Utility function to check whether this site is backed-up by an ESGF node.'''
        
        return self.hasConfig(SECTION_ESGF)
    
    def isGlobusEnabled(self):
        '''Utility function to check whether Globus has been configured for this CoG installation.'''
        
        return self.hasConfig(SECTION_GLOBUS)

    
    
siteManager = SiteManager()
            