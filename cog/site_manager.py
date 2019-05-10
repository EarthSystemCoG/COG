import os
import time
import ConfigParser
import logging

from cog.constants import (SECTION_ESGF, SECTION_GLOBUS, SECTION_PID)

log = logging.getLogger(__name__)

class SiteManager(object):
    '''
    Class used to load site-specific settings at COG startup.
    '''
    
    # location of site specific settigs configuration file
    COG_CONFIG_DIR = os.getenv('COG_CONFIG_DIR', '/usr/local/cog/cog_config')
    CONFIGFILEPATH = os.path.join(COG_CONFIG_DIR, 'cog_settings.cfg')

    def __init__(self):
        '''Initialization method reads the configuration file.'''
        
        # wait for configuration file to be available
        while not os.path.exists( SiteManager.CONFIGFILEPATH ):
            logging.info("Waiting to read configuration file: %s" % SiteManager.CONFIGFILEPATH )
            time.sleep(1)

        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        # location of site specific settings configuration file
        self.cog_config_dir = SiteManager.COG_CONFIG_DIR
        try:
            config = self.config.read( SiteManager.CONFIGFILEPATH )
            logging.info("Site manager: using CoG settings from file(s): %s" % config)
            log.debug('Initialized CoG settings from file: %s' % SiteManager.CONFIGFILEPATH)
            
        except Exception as e:
            log.debug("Error reading site settings configuration file: %s" % SiteManager.CONFIGFILEPATH)

    def get(self, name, section='DEFAULT', default=None):
        '''Method that retrieves a settings value from a specified section of the configuration file.'''
        
        if self.config.has_option(section, name):
            return self.config.get(section, name)
        else:
            return default

    def hasConfig(self, section):
        '''Returns True if the configuration file contains the named section.'''

        return self.config.has_section(section)

    def hasOption(self, section, option):
        '''Returns True if the configuration file contains the named section and the named option.'''

        return self.config.has_option(section, option)

    def isEsgfEnabled(self):
        '''Utility function to check whether this site is backed-up by an ESGF node.'''
        
        return self.hasConfig(SECTION_ESGF)
    
    def isGlobusEnabled(self):
        '''Utility function to check whether Globus has been configured for this CoG installation.'''
        
        return self.hasConfig(SECTION_GLOBUS)

    def isPidEnabled(self):
        '''Utility function to check whether this site has been configured for data cart PIDs.'''

        try:
            __import__('esgfpid')
            module_found = True
        except ImportError:
            module_found = False

        return self.hasOption(SECTION_PID, 'PID_CREDENTIALS') and module_found


siteManager = SiteManager()
