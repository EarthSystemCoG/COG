'''
Class representing a peer COG site.
This class is a wrapper around the django 'Site' object
with additional boolean flag for enabled status.
'''

from django.db import models
from django.contrib.sites.models import Site
from cog.models.constants import APPLICATION_LABEL

class PeerSite(models.Model):
    
    site = models.OneToOneField(Site, blank=False, null=False, related_name='peersite')
    enabled = models.BooleanField(default=False, null=False)
    
    class Meta:
        app_label= APPLICATION_LABEL
        
    def __unicode__(self):
        #return "Site name: %s domain: %s enabled: %s" % (self.site.name, self.site.domain, self.enabled)
        return self.site.name
    
def getPeerSites():
    '''Returns a list of ENABLED peer site objects.'''
    
    # filter PeerSites by enabled=True
    return [peer.site for peer in PeerSite.objects.filter(enabled=True)]



