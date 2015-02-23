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
       from one or more files on the local file system.'''

    def __init__(self, filepath_string):
        
        # split into one or more file paths
        filepaths = filepath_string.replace(' ','').split(",")

        # internal fields
        self.filepaths = filepaths
        self.modtimes = {}  # keyed by file path
        self.idps = {}      # keyed by file spath
        
        # loop over whitelist files
        for filepath in self.filepaths:
            
            # record last modification time
            self.modtimes[filepath] = file_modification_datetime(filepath)

            # load this white list for the first time
            self._reload(filepath, force=True)


    def _reload(self, filepath, force=False):
        '''Internal method to reload an IdP white list if it has changed since it was last read'''

        modtime = file_modification_datetime(filepath)

        if force or modtime > self.modtimes[filepath]:

            print 'Loading IdP white list: %s, last modified: %s' % (filepath, modtime)
            self.modtimes[filepath] = modtime
            idps = []

            # read whitelist
            with open (filepath, "r") as myfile:
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

            # switch the list for this file path
            self.idps[filepath] = idps

    def trust(self, openid):

        # loop over trusted lists
        for filepath in self.filepaths:
            
            # reload the list ?
            self._reload(filepath)
            
            # loop over IdPs in this white list
            for idp in self.idps[filepath]:
                
                # trust this openid
                if openid.lower().startswith(idp):
                    return True

        # don't trust this openid
        return False