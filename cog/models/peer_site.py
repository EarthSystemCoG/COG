"""
Class representing a peer node.
This class is a wrapper around the django 'Site' object
with additional boolean flag for enabled status.
"""

from django.db import models
from django.contrib.sites.models import Site
from cog.models.constants import APPLICATION_LABEL

class PeerSite(models.Model):
    
    site = models.OneToOneField(Site, blank=False, null=False, related_name='peersite', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False, null=False)
    
    class Meta:
        app_label= APPLICATION_LABEL
        
    def __unicode__(self):
        # return "Node name: %s domain: %s enabled: %s" % (self.site.name, self.site.domain, self.enabled)
        return self.site.name


def getPeerSites():
    """Returns a list of ENABLED peer node objects."""
    
    # filter PeerSites by enabled=True
    return [peer.site for peer in PeerSite.objects.filter(enabled=True).order_by('site__name')]



