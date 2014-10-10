'''
CoG configuration script.
This class creates or updates the CoG settings file $COG_CONFIG_DIR/cog_settings.cfg, 
but it does NOT override existing settings.

Settings imported from /esg/config/esgf.properties, unless already found in cog_settings.cfg:
esgf.host=esg-datanode.jpl.nasa.gov:
    - SITE_NAME = ESG-DATANODE.JPL.NASA.GOV
    - SITE_DOMAIN = esg-datanode.jpl.nasa.gov:8000
    - DEFAULT_SEARCH_URL = http://esg-datanode.jpl.nasa.gov/esg-search/search/
db.user=...
    - DATABASE_USER=...
db.port=5432
    - DATABASE_PORT=5432
    
The postgres database password is read from the file /esg/config/.esg_pg_pass

'''

import os
import ConfigParser
import logging
import collections
import StringIO
from constants import SECTION_DEFAULT, ESGF_PROPERTIES_FILE, ESGF_PASSWORD_FILE, DEFAULT_PROJECT_SHORT_NAME

# location of site specific settigs configuration file
COG_CONFIG_DIR = os.getenv('COG_CONFIG_DIR', '/usr/local/cog')
CONFIGFILEPATH = os.path.join(COG_CONFIG_DIR, 'cog_settings.cfg')


class CogConfig(object):
    
    def __init__(self):
        
        # FIXME
        self.esgf = True
    
    def config(self):
        '''Driver method.'''
        
        self._readCogConfig()
        self._readEsgfConfig()
        self._setupConfig()
        self._writeCogConfig()
    
    def _readCogConfig(self):
        '''Method that reads an existing COG configuration file, or create a new one if not existing.'''
        
        # initialize COG configuration file
        self.cogConfig = ConfigParser.ConfigParser(allow_no_value=True, 
                                                   dict_type=collections.OrderedDict)
        # must set following line explicitly to preserve the case of configuration keys
        self.cogConfig.optionxform = str 
        
        # create configuration directory if not existing already
        if not os.path.exists(COG_CONFIG_DIR):
            os.makedirs( COG_CONFIG_DIR )
            logging.debug("Created configuration directory: %s" % COG_CONFIG_DIR )
        
        # read existing configuration file
        try:
            filenames = self.cogConfig.read( CONFIGFILEPATH )
            if len(filenames)>0:
                logging.info("Using existing configuration file: %s" % CONFIGFILEPATH )
            else:
                logging.info("Configuration file: %s not found, will create new one" % CONFIGFILEPATH )
            
        except Exception as e:
            print e
            logging.error("Error reading configuration file: %s" % CONFIGFILEPATH)
            logging.error(e)

        
    def _readEsgfConfig(self):
        '''Method that reads local parameters from ESGF configuration file esgf.properties.'''
        
        # read ESGF configuration file, if available
        self.esgfConfig = ConfigParser.ConfigParser()
        
        # $esg_config_dir/esgf.properties
        try:
            with open(ESGF_PROPERTIES_FILE, 'r') as f:
                # transform Java properties file into python configuration file: must prepend a section
                config_string = '[%s]\n' % SECTION_DEFAULT + f.read()
            config_file = StringIO.StringIO(config_string)
            self.esgfConfig.readfp(config_file)      
            logging.info("Read ESGF configuration parameters from file: %s" % ESGF_PROPERTIES_FILE)  
        except IOError:
            # file not found
            logging.warn("ESGF properties file: %s not found" % ESGF_PROPERTIES_FILE) 
        
        # $esg_config_dir/.esg_pg_pass
        try:
            with open(ESGF_PASSWORD_FILE, 'r') as f:
                password = f.read().strip()
                self.esgfConfig.set(SECTION_DEFAULT, "DATABASE_PASSWORD", password)
                logging.info("Read ESGF database password from file: %s" % ESGF_PASSWORD_FILE)  
        except IOError:
            # file not found
            logging.warn("ESGF database password file: %s not found" % ESGF_PASSWORD_FILE) 
                
                
    def _safeSet(self, key, value, section=SECTION_DEFAULT):
        '''Method to set a configuration option, without overriding an existing value.'''
        
        if not self.cogConfig.has_section(section):
            if section != SECTION_DEFAULT: 
                self.cogConfig.add_section(section) # "The DEFAULT section is not acknowledged."
            
        if not self.cogConfig.has_option(section, key):
            self.cogConfig.set(section, key, value)
        
    def _safeGet(self, key, default=None, section=SECTION_DEFAULT):
        '''Method to retrieve a value by key, or use a default.'''
        
        try:
            return self.esgfConfig.get(section, key)
        except:
            return default

    def _setupConfig(self):
        '''Method that assigns the CoG settings.'''
        
        '''
        # FIXME
#[esgf]
#ESGF_HOSTNAME=hydra.fsl.noaa.gov
#ESGF_DBURL=postgresql://dbsuper:dbpwd@localhost/esgcet
#IDP_WHITELIST=/esg/config/esgf_idp_static.xml        
        '''
        
        # [DEFAULT]        
        hostName = self._safeGet("esgf.host", default='localhost') 
        self._safeSet('SITE_NAME', hostName.upper())
        self._safeSet('SITE_DOMAIN', hostName + ":8000") # FIXME after Apache integration
        self._safeSet('TIME_ZONE', 'America/Denver')
        self._safeSet('SECRET_KEY','<change this to a random sequence of characters 20 or more and dont share it>')
        self._safeSet('COG_MAILING_LIST','cog_info@list.woc.noaa.gov')
        if self.esgf: # ESGF: use postgres by default
            self._safeSet('DJANGO_DATABASE','postgres')
        else:         # no ESGF: use sqllite3 by default
            self._safeSet('DJANGO_DATABASE','sqllite3')
        # if DJANGO_DATABASE=sqllite3
        self._safeSet('DATABASE_PATH','/usr/local/cog/django.data')
        # if DJANGO_DATABASE=postgres
        self._safeSet('DATABASE_NAME', 'cogdb')
        self._safeSet('DATABASE_USER', self._safeGet("db.user") )
        self._safeSet('DATABASE_PASSWORD', self._safeGet("db.password"))
        self._safeSet('DATABASE_PORT', self._safeGet("db.port", default='5432'))
        
        self._safeSet('MEDIA_ROOT','/usr/local/cog/site_media')
        # default project to where '/' requests are redirected
        self._safeSet('HOME_PROJECT', DEFAULT_PROJECT_SHORT_NAME)
        # default search service URL, before any project customization
        self._safeSet('DEFAULT_SEARCH_URL','http://%s/esg-search/search/' % hostName)
        # interval between updates of user's projects, during user session
        self._safeSet('MY_PROJECTS_REFRESH_SECONDS', 600)
        # optional number of days after which password expire
        self._safeSet('PASSWORD_EXPIRATION_DAYS','0')
        # optional top-level URL to redirect user registration (no trailing '/')
        self._safeSet('IDP_REDIRECT','') # no redirect by default
                
    def _writeCogConfig(self):
        '''Method to write out the new CoG configuration.'''
        
        # backup existing file
        if os.path.exists( CONFIGFILEPATH ):
            # FIXME
            #os.rename(self.cogConfigFilePath, self.cogConfigFilePath + "-backup-%s" % time.strftime('%Y-%m-%d_%H:%M:%S'))  
            os.rename(CONFIGFILEPATH, CONFIGFILEPATH + "-backup")  
                
        cfgfile = open(CONFIGFILEPATH,'w')
        self.cogConfig.write(cfgfile)
        cfgfile.close()
        

    
def main():
    
    cogConfig = CogConfig()
    cogConfig.config()

    
if __name__ == '__main__':
    main()