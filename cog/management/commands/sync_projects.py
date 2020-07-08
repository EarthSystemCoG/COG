'''
Django management command to update the status of remote projects from CoG peer sites.
Execute as:
python manage.py sync_projects
'''

from django.core.management.base import BaseCommand
from cog.project_manager import projectManager
import datetime

class Command(BaseCommand):
    
    help = 'Updates the list of projects from remote CoG peers'
       
    def handle(self, *ags, **options):
        
        sites = projectManager.sync()
        print('sync_projects: time=%s synchronized projects from sites=%s' % (datetime.datetime.now(), sites))