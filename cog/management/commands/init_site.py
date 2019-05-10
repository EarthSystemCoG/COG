'''
Django management command to execute initialization tasks for the current site.
Execute as:
python manage.py init_site
Must be executed every time the site configuration changes.
'''

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.conf import settings

import logging

log = logging.getLogger(__name__)

class Command(BaseCommand):
    
    help = 'Initializes the current site'
       
    def handle(self, *ags, **options):
        
        current_site = Site.objects.get_current()
        current_site.name = settings.SITE_NAME
        current_site.domain = settings.SITE_DOMAIN
        current_site.save()

        log.info('Updated current site: name=%s domain=%s' % (current_site.name, current_site.domain))