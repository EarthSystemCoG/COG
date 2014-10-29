'''
Database installation script. 
It uses the configuration settings from $COG_CONFIG_DIR/cog_settings.cfg
'''

import os
import cog
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        
from django.contrib.auth.models import User

from django.contrib.sites.models import Site

from cog.models import Project
from cog.models import UserProfile
from cog.views.views_project import initProject

from cog.installation.constants import DEFAULT_PROJECT_SHORT_NAME

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
        management.call_command("syncdb", interactive=False)
        management.call_command("migrate", "cog")
        management.call_command("collectstatic", interactive=False)
        
        # custom management commands
        management.call_command("init_site")
        management.call_command("sync_sites")
        
    def _createPostgresDB(self):
        '''Method to create the Postgres database if not existing already.'''
        
        dbname = self.siteManager.get('DATABASE_NAME')
        dbuser = self.siteManager.get('DATABASE_USER')
        dbpassword = self.siteManager.get('DATABASE_PASSWORD')
        dbport = self.siteManager.get('DATABASE_PORT')
        dburl = 'postgresql://%s:%s@localhost:%s/postgres' % (dbuser, dbpassword, dbport)
    
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
        
        # Administrator user
        if User.objects.count() == 0:
        #if not User.objects.filter(username='admin').exists():
            logging.info("Creating admin user")
            user = User(first_name='Admin', last_name='User', username='admin', email='adminuser@test.com', 
                        is_staff=True, is_superuser=True)
            user.set_password('changeit')
            user.save()
            userp = UserProfile(user=user, institution='Institution', city='City', state='State', country='Country',
                                site=site,
                                last_password_update=datetime.datetime.now())
            userp.clearTextPassword='changeit' # needed by esgfDatabaseManager, NOT saved as clear text in any database
            userp.save()
            
if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    installer = CoGInstall()
    installer.install()
