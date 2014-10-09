'''
Created on Oct 8, 2014

@author: cinquini
'''

# setup CoG settings first
import os
import cog
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import ConfigParser
import logging
import datetime
import collections
import StringIO
import shutil
from django.core import management
from django.contrib.auth.models import User

from cog.models import Project
from cog.models import UserProfile
from django.contrib.sites.models import Site

logging.basicConfig(level=logging.DEBUG)

SECTION_DEFAULT = 'DEFAULT'
SECTION_ESGF = 'esgf'

ESGF_PROPERTIES_FILE = '/esg/config/esgf.properties'

class CogConfig(object):
    
    def __init__(self):
        
        #os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        pass
    
    def run(self):
        '''Driver method.'''
        
        # FIXME
        self._readCogConfig()
        self._readEsgfConfig()
        self._setupConfig()
        self._writeCogConfig()
        self._upgradeCog()
        self._createObjects()
    
    def _readCogConfig(self):
        '''Method that reads an existing COG configuration file, or create a new one if not existing.'''
        
        # initialize COG configuration file
        self.cogConfigDir = os.getenv('COG_CONFIG_DIR', '/usr/local/cog')
        self.cogConfigFilePath = os.path.join(self.cogConfigDir, 'cog_settings.cfg')
        self.cogConfig = ConfigParser.ConfigParser(allow_no_value=True, 
                                                dict_type=collections.OrderedDict)
        # must set following line explicitly to preserve the case of configuration keys
        self.cogConfig.optionxform = str 
        
        # create configuration directory if not existing already
        if not os.path.exists(self.cogConfigDir):
            os.makedirs( self.cogConfigDir )
            logging.debug("Created configuration directory: %s" % self.cogConfigDir )
        
        # read existing configuration file
        try:
            filenames = self.cogConfig.read( self.cogConfigFilePath )
            if len(filenames)>0:
                logging.info("Using existing configuration file: %s" % self.cogConfigFilePath )
            else:
                logging.info("Configuration file: %s not found, will create new one" % self.cogConfigFilePath )
            
        except Exception as e:
            print e
            logging.error("Error reading configuration file: %s" % self.cogConfigFilePath)
            logging.error(e)

        
    def _readEsgfConfig(self):
        '''Method that reads local parameters from ESGF configuration file esgf.properties.'''
        
        # read ESGF configuration file, if available
        self.esgfConfig = ConfigParser.ConfigParser()
        
        try:
            with open(ESGF_PROPERTIES_FILE, 'r') as f:
                # transform Java properties file into python configuration file: must prepend a section
                config_string = '[%s]\n' % SECTION_DEFAULT + f.read()
                #print config_string
            config_file = StringIO.StringIO(config_string)
            self.esgfConfig.readfp(config_file)        
        except IOError:
            pass # file not found
                
                
    def _safeSet(self, key, value, section=SECTION_DEFAULT):
        '''Method to set a configuration option, without overriding an existing value.'''
        
        if not self.cogConfig.has_section(section):
            if section != SECTION_DEFAULT: 
                self.cogConfig.add_section(section) # "The DEFAULT section is not acknowledged."
            
        if not self.cogConfig.has_option(section, key):
            self.cogConfig.set(section, key, value)
        
    def _safeGet(self, key, defaultValue=None, section=SECTION_DEFAULT):
        '''Method to retrieve a value by key, or use a default.'''
        
        try:
            return self.esgfConfig.get(section, key)
        except:
            return defaultValue

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
        hostName = self._safeGet("esgf.host", defaultValue='localhost') 
        self._safeSet('SITE_NAME', hostName.upper())
        self._safeSet('SITE_DOMAIN', hostName + ":8000") # FIXME after Apache integration
        self._safeSet('TIME_ZONE', 'America/Denver')
        self._safeSet('SECRET_KEY','<change this to a random sequence of characters 20 or more and dont share it>')
        self._safeSet('COG_MAILING_LIST','cog_info@list.woc.noaa.gov')
        
        self._safeSet('DJANGO_DATABASE','sqllite3')
        # if DJANGO_DATABASE=sqllite3
        self._safeSet('DATABASE_PATH','/usr/local/cog/django.data')
        # if DJANGO_DATABASE=postgres
        
        self._safeSet('MEDIA_ROOT','/usr/local/cog/site_media')
        # defeault project to where '/' requests are redirected
        self._safeSet('HOME_PROJECT', 'cog')
        # default search service URL, before any project customization
        self._safeSet('DEFAULT_SEARCH_URL','http://%s/esg-search/search/' % hostName)
        # interval between updates of user's projects, during user session
        self._safeSet('MY_PROJECTS_REFRESH_SECONDS', 600)
        # optional number of days after which password expire
        self._safeSet('PASSWORD_EXPIRATION_DAYS','0')
        # optional top-level URL to redirect user registration (no trailing '/')
        self._safeSet('IDP_REDIRECT','') # no redirect by default
        
        # FIXME: read values from ESGF files
        self._safeSet('DATABASE_NAME', 'cogdb2')
        self._safeSet('DATABASE_USER', '<CoG database user>')
        self._safeSet('DATABASE_NAME', '<CoG database password>')
        self._safeSet('PASSWORD_PORT', '5432')
        
    def _writeCogConfig(self):
        '''Method to write out the new CoG configuration.'''
        
        # backup existing file
        if os.path.exists(self.cogConfigFilePath):
            # FIXME
            #os.rename(self.cogConfigFilePath, self.cogConfigFilePath + "-backup-%s" % time.strftime('%Y-%m-%d_%H:%M:%S'))  
            os.rename(self.cogConfigFilePath, self.cogConfigFilePath + "-backup")  
                
        cfgfile = open(self.cogConfigFilePath,'w')
        self.cogConfig.write(cfgfile)
        cfgfile.close()
        
    def _upgradeCog(self):
        '''Method to run the necessary Django management commands to upgrade the CoG installation.'''
        
        cogpath = os.path.dirname(cog.__file__)
        
        # create database if not existing already
        # FIXME ?
        dbtype = self.cogConfig.get(SECTION_DEFAULT, 'DJANGO_DATABASE')
        if dbtype=='sqllite3':
            dbpath = self.cogConfig.get(SECTION_DEFAULT, 'DATABASE_PATH')
            if not os.path.exists(dbpath):
                shutil.copyfile('%s/../database/django.data' % cogpath, dbpath) # directory parallel to 'cog' module
        else:
            pass
        
        management.call_command("syncdb", interactive=False)
        management.call_command("migrate", "cog")
        management.call_command("collectstatic", interactive=False)
        
    def _createObjects(self):
        '''Method to populate the database with some initial objects.'''
        
        # Site
        site = Site.objects.create(name='localhost', domain='localhost:8000')
        site.save()
        
        # Test project
        project = Project.objects.create(short_name='TestProject', long_name='Test Project', site=site, active=True)
        project.save()
        
        # Administrator user
        user = User.objects.create(first_name='Admin', last_name='User', username='admin', email='adminuser@test.com', 
                                   is_staff=True, is_superuser=True)
        user.set_password( 'changeit' )
        user.save()
        userProfile = UserProfile.objects.create(user=user, 
                                                 institution='Institution', city='City', state='State', country='Country',
                                                 last_password_update=datetime.datetime.now())
        userProfile.save()
    
def main():
    
    cogConfig = CogConfig()
    cogConfig.run()

    
if __name__ == '__main__':
    main()