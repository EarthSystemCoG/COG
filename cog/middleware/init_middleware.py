# Module containing middleware to run code when django first starts up

from django.core.exceptions import MiddlewareNotUsed
from cog.plugins.esgf.registry import PeerNodesList
from cog.site_manager import siteManager

class InitMiddleware(object):

    def __init__(self):
        
        print 'Executing CoG initialization tasks'
        
        # update list of ESGF peers into database
        filepath = siteManager.get('PEER_NODES')
        pnl = PeerNodesList(filepath)
        pnl.reload() # delete=False
        
        # read IdP whitelist
        
        # remove this class from the middleware that is invoked for every request
        raise MiddlewareNotUsed('Do not invoke ever again')
        
    def process_request(self, request):
        print 'This line should never be printed...'
        return None