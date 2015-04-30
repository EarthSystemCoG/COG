'''
Module containing API and implementation for OpenID white-listing.
'''

from xml.etree.ElementTree import fromstring
import re
import abc
#import pycurl
#import certifi
from cog.utils import file_modification_datetime
from django.conf import settings
import os

NS = "http://www.esgf.org/whitelist"

class WhiteList(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def trust(self, openid):
        '''Returns true if an openid can be trusted, false otherwise.'''
        pass
    
class KnownProvidersDict(object):
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def idpDict(self):
        '''Returns a dictionary of (IdP name, IdP URL) pairs.''' 
        pass
    
class EndpointDict(object):

    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def endpointDict(self):
        '''Returns a dictionary of (GridFTP hostname:port, Globus endpoint name) pairs.''' 
        pass
    
class LocalEndpointDict(EndpointDict):
    '''Implementation of EndpointDict based on a local XML configuration file.'''
    
    def __init__(self, filepath):
        
        self.endpoints = {}
        self.init = False
        
        try:
            if os.path.exists(filepath):
                self.filepath = filepath
                self.modtime = file_modification_datetime(self.filepath)
                self._reload(force=True)
                self.init = True
            
        except IOError:
            pass
        
    def _reload(self, force=False):
        '''Internal method to reload the dictionary of endpoints if the file has changed since it was last read'''

        modtime = file_modification_datetime(self.filepath)

        if force or modtime > self.modtime:

            print 'Loading endpoints from: %s, last modified: %s' % (self.filepath, modtime)
            self.modtime = modtime
            endpoints = {}

            # read XML file
            with open (self.filepath, "r") as myfile:
                xml=myfile.read().replace('\n', '')
                
            # <endpoints xmlns="http://www.esgf.org/whitelist">
            root = fromstring(xml)
            # <endpoint name="esg#jpl" gridftp="esg-datanode.jpl.nasa.gov:2811" />
            for endpoint in root.findall("{%s}endpoint" % NS):
                gridftp = endpoint.attrib['gridftp']
                name = endpoint.attrib['name']
                endpoints[ gridftp ] = name
                print 'Using endpoint: %s --> %s' % (gridftp, name)

            # switch the dictionary of endpoints after reading
            self.endpoints = endpoints
    
    def endpointDict(self):
        
        self._reload() # reload dictionary from file ?
        return self.endpoints

    
class LocalKnownProvidersDict(KnownProvidersDict):
    '''Implementation of KnownProvidersDict based on a local XML configuration file.'''
    
    def __init__(self):
        
        # internal dictionary of known identity providers (empty by default)
        self.idps = {} # (IdP name, IdP url)
        self.init = False
        
        try:
            
            # store filepath and its last access time
            self.filepath = str(settings.KNOWN_PROVIDERS)
            
            if os.path.exists(self.filepath):
                
                self.init = True # file of known providers is found
                self.modtime = file_modification_datetime(self.filepath)
                
                # load dictionary at startup
                self._reload(force=True)
            
        except AttributeError:
            # no entry in $COG_CONFIG_DIR/cog_settings.cfg
            pass
            
        
    def idpDict(self):
        
        # reload dictionary from file ?
        self._reload()
        return self.idps
        
    def _reload(self, force=False):
        '''Internal method to reload the dictionary of known IdPs if it has changed since it was last read'''

        if self.init: # file exists
            
            modtime = file_modification_datetime(self.filepath)
    
            if force or modtime > self.modtime:
    
                print 'Loading known IdPs from file: %s, last modified: %s' % (self.filepath, modtime)
                self.modtime = modtime
                idps = {}
    
                # read whitelist
                with open (self.filepath, "r") as myfile:
                    xml=myfile.read().replace('\n', '')
    
                # <OPS>
                root = fromstring(xml)
                
                #  <OP>
                #    <NAME>NASA Jet Propulsion Laboratory (JPL)</NAME>
                #    <URL>https://esg-datanode.jpl.nasa.gov/esgf-idp/openid/</URL>
                #  </OP>
                for idp in root.findall("OP"):
                    name = idp.find('NAME').text
                    url = idp.find('URL').text
                    idps[name] = url
                    print 'Using known IdP: name=%s url=%s' % (name, url)
    
                # switch the dictionary of knwon providers
                self.idps = idps

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