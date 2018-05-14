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
db.host=localhost
    - DATABASE_HOST=localhost
db.port=5432
    - DATABASE_PORT=5432
mail.admin.address=esg-node@jpl.nasa.gov
    - EMAIL_SENDER=esg-node@jpl.nasa.gov
      (also used as default email of site administrator)

The postgres database password is read from the file /esg/config/.esg_pg_pass
    - DATABASE_PASSWORD

'''

import ConfigParser
import StringIO
import collections
import logging
import os
import time
from django.utils.crypto import get_random_string

from constants import (SECTION_DEFAULT, COG_SECTION_DEFAULT, SECTION_ESGF, SECTION_EMAIL,
                       ESGF_PROPERTIES_FILE, ESGF_PASSWORD_FILE,
                       IDP_WHITELIST, KNOWN_PROVIDERS, PEER_NODES,
                       DEFAULT_PROJECT_SHORT_NAME)


# location of site specific settings configuration file
COG_CONFIG_DIR = os.getenv('COG_CONFIG_DIR', '/usr/local/cog/cog_config')
CONFIGFILEPATH = os.path.join(COG_CONFIG_DIR, 'cog_settings.cfg')

class CogConfig(object):

    def __init__(self, esgfFlag):

        self.esgf = esgfFlag

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
            logging.info("filenames: %s", filenames )
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

        # read ESGF configuration file ($esg_config_dir/esgf.properties), if available
        self.esgfConfig = ConfigParser.ConfigParser()
        try:
            self.esgfConfig.read(ESGF_PROPERTIES_FILE)
        except IOError:
            # file not found
            logging.warn("ESGF properties file: %s not found" % ESGF_PROPERTIES_FILE)
        else:
            #Functionality for ESGF 3.0 where esgf.properties already has a section header called installer.properties
            if SECTION_DEFAULT in self.esgfConfig.sections():
                logging.info("Existing section header found.")
                logging.info("Read ESGF configuration parameters from file: %s" % ESGF_PROPERTIES_FILE)
            else:
                with open(ESGF_PROPERTIES_FILE, 'r') as f:
                    # transform Java properties file into python configuration file: must prepend a section
                    config_string = '[%s]\n' % SECTION_DEFAULT + f.read()
                    config_file = StringIO.StringIO(config_string)
                    self.esgfConfig.readfp(config_file)
                logging.info("Read ESGF configuration parameters from file: %s" % ESGF_PROPERTIES_FILE)


        # $esg_config_dir/.esg_pg_pass
        try:
            with open(ESGF_PASSWORD_FILE, 'r') as f:
                password = f.read().strip()
                # if found, value in .esg_pg_pass will override value from esgf.properties
                self.esgfConfig.set(SECTION_DEFAULT, "db.password", password)
                logging.info("Read ESGF database password from file: %s" % ESGF_PASSWORD_FILE)
        except IOError:
            # file not found
            logging.warn("ESGF database password file: %s could not found or could not be read" % ESGF_PASSWORD_FILE)


    def _safeSet(self, key, value, section=COG_SECTION_DEFAULT, override=False):
        '''Method to set a configuration option, without overriding an existing value
            (unless explicitly requested).'''
        if not self.cogConfig.has_section(section):
            logging.debug("Section %s not found", section)
            if section != COG_SECTION_DEFAULT:
                logging.debug("attempting to add section %s", section)
                self.cogConfig.add_section(section) # "The DEFAULT section is not acknowledged."

        if override or not self.cogConfig.has_option(section, key):
            self.cogConfig.set(section, key, value)

    def _safeGet(self, key, default=None, section=SECTION_DEFAULT):
        '''Method to retrieve a value by key, or use a default.'''

        try:
            return self.esgfConfig.get(section, key)
        except:
            return default

    def _setupConfig(self):
        '''Method that assigns the CoG settings.'''

        # [DEFAULT]
        hostName = self._safeGet("esgf.host", default='localhost')
        self._safeSet('SITE_NAME', hostName.upper())
        self._safeSet('SITE_DOMAIN', hostName)
        self._safeSet('TIME_ZONE', 'America/Denver')
        self._safeSet('SECRET_KEY', get_random_string(length=128))
        self._safeSet('COG_MAILING_LIST','cog_info@list.woc.noaa.gov')
        if self.esgf: # ESGF: use postgres by default
            self._safeSet('DJANGO_DATABASE','postgres')
        else:         # no ESGF: use sqllite3 by default
            self._safeSet('DJANGO_DATABASE','sqllite3')
        # if DJANGO_DATABASE=sqllite3
        self._safeSet('DATABASE_PATH','%s/django.data' % COG_CONFIG_DIR)
        # if DJANGO_DATABASE=postgres
        self._safeSet('DATABASE_NAME', 'cogdb')
        self._safeSet('DATABASE_USER', self._safeGet("db.user"))
        self._safeSet('DATABASE_PASSWORD', self._safeGet("db.password"))
        self._safeSet('DATABASE_HOST', self._safeGet("db.host", default='localhost'))
        self._safeSet('DATABASE_PORT', self._safeGet("db.port", default='5432'))
        self._safeSet('MEDIA_ROOT','%s/site_media' % COG_CONFIG_DIR)
        # default project to where '/' requests are redirected
        self._safeSet('HOME_PROJECT', DEFAULT_PROJECT_SHORT_NAME)
        # default search service URL, before any project customization
        self._safeSet('DEFAULT_SEARCH_URL','http://%s/esg-search/search/' % hostName)
        # interval between updates of user's projects, during user session
        self._safeSet('MY_PROJECTS_REFRESH_SECONDS', 3600)
        # optional number of days after which password expire
        self._safeSet('PWD_EXPIRATION_DAYS','0')
        # optional top-level URL to redirect user registration (no trailing '/')
        idpPeer = self._safeGet("esgf.idp.peer", default=None)
        if hostName != idpPeer and idpPeer is not None:
            self._safeSet('IDP_REDIRECT', 'https://%s' % idpPeer) # redirect to specified "esgf.idp.peer"
        else:
            self._safeSet('IDP_REDIRECT','') # no redirect by default
        # DEBUG setting: must be False for production servers to avoid broadcasting detailed system paths
        self._safeSet('DEBUG', 'False')
        # ALLOWED_HOSTS = [] must be included if DEBUG=False
        self._safeSet('ALLOWED_HOSTS', hostName)
        # IDP_WHITELIST = /esg/config/esgf_idp.xml, /esg/config/esgf_idp_static.xml
        self._safeSet('IDP_WHITELIST', IDP_WHITELIST)
        # KNOWN_PROVIDERS = /esg/config/esgf_known_providers.xml
        self._safeSet('KNOWN_PROVIDERS', KNOWN_PROVIDERS)
        # PEER_NODES = /esg/config/esgf_cogs.xml
        self._safeSet('PEER_NODES', PEER_NODES)
        # option to send SESSION and CSRF cookies via SSL only - requires full SSL-encrypted site
        self._safeSet('PRODUCTION_SERVER', True)
        # ESGF software stack version
        esgfVersion = self._safeGet("version", default=None)
        if esgfVersion:
            self._safeSet('ESGF_VERSION', esgfVersion, override=True)
        # option to disable CAPTCHA for creating account in automatic testing
        self._safeSet('USE_CAPTCHA', True)


        #[ESGF]
        if self.esgf:
            self._safeSet('ESGF_HOSTNAME', hostName, section=SECTION_ESGF)
            self._safeSet('ESGF_DBURL',
                          "postgresql://%s:%s@%s/esgcet" % (self._safeGet("db.user"), self._safeGet("db.password"), self._safeGet("db.host")),
                          section=SECTION_ESGF)

        #[EMAIL]
        self._safeSet('EMAIL_SERVER', self._safeGet("mail.smtp.host"), section=SECTION_EMAIL)
        self._safeSet('EMAIL_PORT', '', section=SECTION_EMAIL)
        self._safeSet('EMAIL_SENDER', self._safeGet("mail.admin.address", default='CoG@%s' % hostName), section=SECTION_EMAIL)
        self._safeSet('EMAIL_USERNAME', '', section=SECTION_EMAIL)
        self._safeSet('EMAIL_PASSWORD', '', section=SECTION_EMAIL)
        self._safeSet('EMAIL_SECURITY', 'STARTTLS', section=SECTION_EMAIL)


    def _writeCogConfig(self):
        '''Method to write out the new CoG configuration.'''

        # backup existing file
        if os.path.exists( CONFIGFILEPATH ):
            os.rename(CONFIGFILEPATH, CONFIGFILEPATH + "-backup-%s" % time.strftime('%Y-%m-%d_%H:%M:%S'))

        cfgfile = open(CONFIGFILEPATH,'w')
        self.cogConfig.write(cfgfile)
        cfgfile.close()
        logging.info("Written CoG configuration file: %s" % CONFIGFILEPATH)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    cogConfig = CogConfig(False) # esgfFlag
    cogConfig.config()
