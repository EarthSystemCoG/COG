# Module containing middleware to run code when django first starts up

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import MiddlewareNotUsed
from cog.plugins.esgf.registry import PeerNodesList
from cog.site_manager import siteManager

import logging

log = logging.getLogger(__name__)

class InitMiddleware(object):

    def __init__(self):

        log.debug('Executing CoG initialization tasks')

        # update name, domain of current site into database
        current_site = Site.objects.get_current()
        current_site.name = settings.SITE_NAME
        current_site.domain = settings.SITE_DOMAIN
        current_site.save()
        log.debug('Updated current site: name=%s domain=%s' % (current_site.name, current_site.domain))

        # update list of ESGF peers into database
        filepath = siteManager.get('PEER_NODES')
        try:
            pnl = PeerNodesList(filepath)
            pnl.reload() # delete=False
        except Exception as error:
            log.error("Could not update peer nodes from xml file: %s" % str(error))

        # read IdP whitelist

        # remove this class from the middleware that is invoked for every request
        raise MiddlewareNotUsed('Do not invoke ever again')

    def process_request(self, request):
        log.error('This line should never be printed...')
        return None
