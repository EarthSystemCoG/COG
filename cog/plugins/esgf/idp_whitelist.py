'''
Middleware that enforces an IdP white-list during openID authentication.
'''

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from xml.etree.ElementTree import fromstring
import re
import abc
from cog.utils import file_modification_datetime

NS = "http://www.esgf.org/whitelist"

class WhiteList(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def trust(self, openid):
        '''Returns true if an openid can be trusted, false otherwise.'''
        pass

class LocalWhiteList(WhiteList):
    '''Whitelist implementation that reads the list of trusted IdPs
       from a file on the local file system.'''

    def __init__(self, filepath):

        # internal fields
        self.idps = []
        self.filepath = filepath
        self.modtime = file_modification_datetime(self.filepath)

        # load white list for the first time
        self._reload(force=True)


    def _reload(self, force=False):
        '''Internal method to reload the IdP white list if it has changed since it was last read'''

        modtime = file_modification_datetime(self.filepath)

        if force or modtime > self.modtime:

            print 'Loading IdP white list: %s, last modified: %s' % (self.filepath, modtime)
            self.modtime = modtime
            idps = []

            # read whitelist
            with open (self.filepath, "r") as myfile:
                xml=myfile.read().replace('\n', '')

            # <idp_whitelist xmlns="http://www.esgf.org/whitelist">
            root = fromstring(xml)
            # <value>https://hydra.fsl.noaa.gov/esgf-idp/idp/openidServer.htm</value>
            for value in root.findall("{%s}value" % NS):
                match = re.search('(https://[^\/]*/)', value.text)
                if match:
                    idp = match.group(1)
                    idps.append(idp.lower())
                    print 'Using trusted IdP: %s' % idp

            # switch the list
            self.idps = idps

    def trust(self, openid):

        # reload the white list ?
        self._reload()

        # loop over trusted IdPs
        for idp in self.idps:
            # trust this openid
            if openid.lower().startswith(idp):
                return True

        # don't trust this openid
        return False



class IdpWhitelistMiddleware(object):

    def __init__(self):

        # initialize the white list service
        self.whitelist = LocalWhiteList(settings.IDP_WHITELIST)

        # '/openid/complete/'
        self.url = reverse('openid-login')


    def process_request(self, request):

        # intercept only these requests
        if request.path == self.url:

            openid_identifier = request.REQUEST.get('openid_identifier', None)
            next = request.REQUEST.get('next', "/") # preserve 'next' redirection after successful login
            if openid_identifier is not None:

                # invalid OpenID
                if not openid_identifier.lower().startswith('https'):
                    return HttpResponseRedirect(reverse('openid-login')+"?message=invalid_openid&next=%s" % next)

                # invalid IdP
                if not self.whitelist.trust(openid_identifier):
                    return HttpResponseRedirect(reverse('openid-login')+"?message=invalid_idp&next=%s" % next)

        # keep on processing this request
        return None

if __name__ == '__main__':

    IdpWhitelistMiddleware()
