'''
Database installation script. 
It uses the configuration settings from $COG_CONFIG_DIR/cog_settings.cfg
'''

import os
import cog
from cog.constants import SECTION_EMAIL
from django.conf import settings
        
from django.contrib.auth.models import User

from django.contrib.sites.models import Site

from cog.models import Project
from cog.models import UserProfile
from cog.models import PeerSite
from cog.views.views_project import initProject

from cog.installation.constants import (DEFAULT_PROJECT_SHORT_NAME, ESGF_ROOTADMIN_PASSWORD_FILE, 
                                        DEFAULT_ROOTADMIN_PWD, ROOTADMIN_USERNAME, ROOTADMIN_GROUP,
                                        ROOTADMIN_ROLE)

from cog.services.registration.registration_impl import esgfRegistrationServiceImpl
from cog.plugins.esgf.security import esgfDatabaseManager
from django_openid_auth.models import UserOpenID
from django.core.exceptions import ObjectDoesNotExist

from django.core import management
import sqlalchemy
import datetime
import logging

from cog.site_manager import SiteManager

class CoGInstall(object):
    '''
    Class that initializes, populates and upgrades the CoG database.
    '''
    
    def __init__(self):
                
        # read cog_settings.cfg
        self.siteManager = SiteManager()
    
    def install(self):
        '''Driver method.'''
        
        self._upgradeCog()
        self._createObjects()

    def _upgradeCog(self):
        '''Method to run the necessary Django management commands to upgrade the CoG installation.'''
        
        #cogpath = os.path.dirname(cog.__file__)
        
        # create database if not existing already
        dbtype = self.siteManager.get('DJANGO_DATABASE')
        if dbtype=='sqllite3':
            pass # database will be created automatically

        elif dbtype=='postgres':
            self._createPostgresDB()
            
        else:
            raise Exception("Unknow database type: %s" % dbtype)
        
        # django management commands
        #management.call_command("syncdb", interactive=False)
        #management.call_command("migrate","--fake-initial")
        management.call_command("migrate", interactive=False)
        management.call_command("collectstatic", interactive=False, verbosity=0)
        
        # custom management commands
        management.call_command("init_site")
        management.call_command("sync_sites")  # updates list of CoG peers from sites.xml
        
    def _createPostgresDB(self):
        '''Method to create the Postgres database if not existing already.'''
        
        dbname = self.siteManager.get('DATABASE_NAME')
        dbuser = self.siteManager.get('DATABASE_USER')
        dbpassword = self.siteManager.get('DATABASE_PASSWORD')
        dbhost = self.siteManager.get('DATABASE_HOST')
        dbport = self.siteManager.get('DATABASE_PORT')
        dburl = 'postgresql://%s:%s@%s:%s/postgres' % (dbuser, dbpassword, dbhost, dbport)
    
        # connect to the 'postgres' database
        engine = sqlalchemy.create_engine(dburl)
        conn = engine.connect()
        # must end current transaction before creating a new database
        conn.execute("commit")
        
        # create new database if not existing already
        try:
            conn.execute("create database %s with owner=%s" % (dbname, dbuser))
            logging.info("Postgres database: %s created" % dbname)
        except sqlalchemy.exc.ProgrammingError as e:
            logging.warn(e)
            logging.info("Postgres database: %s already exists" % dbname)
 
        conn.close()
        
    def _createObjects(self):
        '''Method to populate the database with some initial objects.'''
                
        # Site: reuse default site 'example.com'
        site = Site.objects.get(pk=1)
        logging.info("Updating site: %s" % site)
        site.name = self.siteManager.get('SITE_NAME')
        site.domain = self.siteManager.get('SITE_DOMAIN')
        site.save()
        
        # Test project
        #if not Project.objects.filter(short_name=DEFAULT_PROJECT_SHORT_NAME).exists():
        if Project.objects.count() == 0:
            logging.info("Creating project: %s" % DEFAULT_PROJECT_SHORT_NAME)
            project = Project.objects.create(short_name=DEFAULT_PROJECT_SHORT_NAME, 
                                             long_name='Test Project', 
                                             description='This is a test project',
                                             site=site, active=True)
            initProject(project)
            project.save()
        
        # create Administrator user - one time only
        if User.objects.count() == 0:
            
            # create User object
            logging.info("Creating admin user")
            user = User(first_name='Admin', last_name='User', 
                        username=ROOTADMIN_USERNAME, 
                        email=self.siteManager.get('EMAIL_SENDER', section=SECTION_EMAIL), 
                        is_staff=True, is_superuser=True)
            if settings.ESGF_CONFIG:
                password = self._getRootAdminPassword()
            else:
                password = DEFAULT_ROOTADMIN_PWD
            user.set_password(password)
            user.save()
                        
            # create UserProfile object
            userp = UserProfile(user=user, institution='Institution', city='City', state='State', country='Country',
                                site=site, last_password_update=datetime.datetime.now())
            userp.clearTextPwd=password # needed by esgfDatabaseManager, NOT saved as clear text in any database
            userp.save()
            
            # ESGF database setup
            if settings.ESGF_CONFIG:
                
                # create rootAdmin openid: https://<ESGF_HOSTNAME>/esgf-idp/openid/rootAdmin
                openid = esgfDatabaseManager.buildOpenid(ROOTADMIN_USERNAME)
                UserOpenID.objects.create(user=user, claimed_id=openid, display_id=openid)
                logging.info("Created openid:%s for CoG administrator: %s" % (openid, user.username) )
                
                # insert rootAdmin user in ESGF database
                logging.info("Inserting CoG administrator: %s in ESGF database" % user.username)
                esgfDatabaseManager.insertEsgfUser(user.profile)
                esgfRegistrationServiceImpl.subscribe(openid, ROOTADMIN_GROUP, ROOTADMIN_ROLE)
                esgfRegistrationServiceImpl.process(openid, ROOTADMIN_GROUP, ROOTADMIN_ROLE, True)
            
        # must create and enable 'esgf.idp.peer" as federated CoG peer
        if settings.IDP_REDIRECT is not None and settings.IDP_REDIRECT.strip()  != '':
            idpHostname = settings.IDP_REDIRECT.lower().replace('http://','').replace('https://','')
            try:
                idpPeerSite = PeerSite.objects.get(site__domain=idpHostname)
                idpPeerSite.enabled=True
                idpPeerSite.save()
            except ObjectDoesNotExist:
                site = Site.objects.create(name=idpHostname, domain=idpHostname)
                idpPeerSite = PeerSite.objects.create(site=site, enabled=True)
            print '\tCreated IdP Peer site: %s with enabled=%s' % (idpPeerSite, idpPeerSite.enabled)

            
    def _getRootAdminPassword(self):
        '''Tries to read the rootAdmin password from the ESGF standard location '/esg/config/.esgf_pass',
        if not found it uses 'changeit'.'''
    
        # /esg/config/.esgf_pass
        try:
            with open(ESGF_ROOTADMIN_PASSWORD_FILE, 'r') as f:
                password = f.read().strip()
                logging.info("Read ESGF administrator password from file: %s" % ESGF_ROOTADMIN_PASSWORD_FILE)  
                return password
        except IOError:
            # file not found
            logging.warn("ESGF administrator password file: %s could not found or could not be read" % ESGF_ROOTADMIN_PASSWORD_FILE) 
            logging.warn("Using standard administrator password, please change it right away.")
            return DEFAULT_ROOTADMIN_PWD

            
if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    installer = CoGInstall()
    installer.install()
