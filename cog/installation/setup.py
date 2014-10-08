'''
Created on Oct 8, 2014

@author: cinquini
'''

import os
import ConfigParser
import logging
import time
import collections

logging.basicConfig(level=logging.DEBUG)

SECTION_DEFAULT = 'DEFAULT'
SECTION_ESGF = 'esgf'

class CogConfig(object):
    
    def __init__(self):
        
        # create or update cog_settings.cfg
        self.configDir = os.getenv('COG_CONFIG_DIR', '/usr/local/cog')
        self.configFilePath = os.path.join(self.configDir, 'cog_settings.cfg')
        self.config = ConfigParser.ConfigParser(allow_no_value=True, 
                                                dict_type=collections.OrderedDict)
        # must set following line explicitely to preserve the case of configuration keys
        self.config.optionxform = str 
        
    def read(self):
        
        # create configuration directory if not existing already
        if not os.path.exists(self.configDir):
            os.makedirs( self.configDir )
            logging.debug("Created configuration directory: %s" % self.configDir )
        
        # read existing configuration file
        try:
            filenames = self.config.read( self.configFilePath )
            if len(filenames)>0:
                logging.info("Using existing configuration file: %s" % self.configFilePath )
   
            else:
                logging.info("Configuration file: %s not found, will create new one" % self.configFilePath )
            
        except Exception as e:
            print e
            logging.error("Error reading configuration file: %s" % self.configFilePath)
            logging.error(e)
        
    
    def _safeSet(self, section, key, value):
        '''Method to set a configuration option, without overriding an existing value.'''
        
        if not self.config.has_section(section):
            if section != SECTION_DEFAULT: 
                self.config.add_section(section) # "The DEFAULT section is not acknowledged."
            
        if not self.config.has_option(section, key):
            self.config.set(section, key, value)
        

    def setup(self):
        
        # [DEFAULT]
        self._safeSet(SECTION_DEFAULT, 'DATABASE_NAME', 'cogdb')
        self._safeSet(SECTION_DEFAULT, 'PASSWORD_EXPIRATION_DAYS', '0')
        self._safeSet(SECTION_DEFAULT, 'HOME_PROJECT', 'cog')
        
        
    def write(self):
        
        # backup existing file
        if os.path.exists(self.configFilePath):
            os.rename(self.configFilePath, self.configFilePath + "-backup-%s" % time.strftime('%Y-%m-%d_%H:%M:%S'))  
                
        cfgfile = open(self.configFilePath,'w')
        self.config.write(cfgfile)
        cfgfile.close()
    
def main():
    
    cogConfig = CogConfig()
    cogConfig.read()
    cogConfig.setup()
    cogConfig.write()
    
if __name__ == '__main__':
    main()