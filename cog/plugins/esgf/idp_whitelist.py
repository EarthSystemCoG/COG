'''
Module containing API and implementation for OpenID white-listing.
'''

from xml.etree.ElementTree import fromstring
import re
import abc
#import pycurl
#import certifi
from cog.utils import file_modification_datetime

NS = "http://www.esgf.org/whitelist"

#curl = pycurl.Curl()
#curl.setopt(pycurl.CAINFO, certifi.where())
#print '\nPYCURL'
#curl.setopt(pycurl.URL, "https://esg-datanode.jpl.nasa.gov/esgf-idp/")
#curl.perform()

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