'''
Django management command to update the list of CoG peer nodes in the local database.
Execute as:
python manage.py update_peers [--delete]
'''

from optparse import make_option
import os
from xml.etree.ElementTree import fromstring

from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from cog.models import PeerSite


FILENAME = "sites.xml" # located in same directory as this command

class Command(BaseCommand):
    
    help = 'Updates the list of CoG peers in the local database'
    
    # add option to delete sites if not found in XML
    option_list = BaseCommand.option_list + (
    make_option('--delete',
        action='store_true',
        dest='delete',
        default=False,
        help='Delete stale sites that are found in database but not in the XML file'),
    )

    
    def handle(self, **options):
        
        
        self.stdout.write('Updating list of CoG sites (delete=%s)' % options['delete'])
                    
        # read sites.xml file located in this directory    
        filepath = os.path.join(os.path.dirname(__file__), FILENAME)
        with open (filepath, "r") as myfile:
            
            xml=myfile.read().replace('\n', '')

            # <sites>
            root = fromstring(xml)
            
            # update/insert all sites found in file
            domains = [] # list of site domains found in file
            for site in root.findall("site"):
                name = site.attrib['name']
                domain = site.attrib['domain']
                domains.append(domain)
                
                # update Site objects
                try:
                    _site = Site.objects.get(domain=domain)
                    # update site
                    _site.name = name
                    _site.save()
                    self.stdout.write('Update site: %s' % _site)
                except ObjectDoesNotExist:
                    _site = Site.objects.create(name=name, domain=domain)
                    self.stdout.write('Created site: %s' % _site)
                    
                # update PeerSite objects
                try:
                    peersite = PeerSite.objects.get(site=_site)
                except ObjectDoesNotExist:
                    peersite = PeerSite.objects.create(site=_site, enabled=False)
                self.stdout.write('\tPeer site: %s' % peersite)
                        
        # clean up stale sites
        if options['delete']:
            for peer in PeerSite.objects.all():
                if peer.site.domain not in domains:
                    self.stdout.write('Stale peer site found at domain: %s' % peer.site.domain + ", deleting it...")
                    peer.site.delete() # will also delete the PeerSite object on cascade

                
