'''
Django management command to update the list of CoG peer nodes in the local database.
Execute as:
python manage.py sync_sites [--delete]
'''

from optparse import make_option
from xml.etree.ElementTree import fromstring

from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from cog.plugins.esgf.registry import PeerNodesList
from cog.site_manager import siteManager


# read /esg/config/esgf_cogs.xml
FILEPATH = siteManager.get('PEER_NODES')

class Command(BaseCommand):

    help = 'Updates the list of CoG peers in the local database'


    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help='Delete stale sites that are found in database but not in the XML file')

    def handle(self, *args, **options):
        try:
            pnl = PeerNodesList(FILEPATH)
            pnl.reload(delete=options['delete'])
        except Exception, error:
            print "Could not update peer nodes from xml file", error
