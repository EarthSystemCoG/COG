'''
Module containing API and implementation for registry-type objects.
'''

import abc
import logging
import os
import re
from xml.etree.ElementTree import fromstring, ParseError

from cog.constants import (IDP_WHITELIST_STATIC_FILENAME, IDP_WHITELIST_FILENAME, 
                           KNOWN_PROVIDERS_FILENAME, PEER_NODES_FILENAME)
from cog.models import PeerSite
from cog.utils import file_modification_datetime, check_filepath
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist


#import pycurl
#import certifi
NS = "http://www.esgf.org/whitelist"
log = logging.getLogger(__name__)

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
                
                # prevent file path manipulation
                check_filepath(self.filepath, [KNOWN_PROVIDERS_FILENAME])
                
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
    
                log.info('Loading known IdPs from file: %s, last modified: %s' % (self.filepath, modtime))
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
                    if name is not None and len(name.strip()) > 0:
                        url = idp.find('URL').text
                        idps[name] = url
                        log.debug('Using known IdP: name=%s url=%s' % (name, url))
    
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
            
            # prevent file path manipulation
            check_filepath(filepath, [IDP_WHITELIST_FILENAME, IDP_WHITELIST_STATIC_FILENAME])
            
            # record last modification time
            self.modtimes[filepath] = file_modification_datetime(filepath)

            # load this white list for the first time
            try:
                self._reload(filepath, force=True)
            except ParseError as e:
                log.error(str(e)) # error from parsing single white-list files and continue


    def _reload(self, filepath, force=False):
        '''Internal method to reload an IdP white list if it has changed since it was last read'''

        modtime = file_modification_datetime(filepath)

        if force or modtime > self.modtimes[filepath]:

            log.info('Loading IdP white list: %s, last modified: %s' % (filepath, modtime))
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
                    log.debug('Using trusted IdP: %s' % idp)

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
    
class PeerNodesList(object):
    '''
    Class that updates the peer nodes in the database from an XML configuration file.
    '''
   
    def __init__(self, filepath):
        
        self.filepath = filepath
        
        # prevent file path manipulation
        check_filepath(self.filepath, [PEER_NODES_FILENAME])

        
    def reload(self, delete=False):
        
        if self.filepath is not None and os.path.exists(self.filepath):
            
            log.info('Updating list of CoG sites from: %s (delete: %s)' % (self.filepath, delete) )
            
            # current site - must not be updated from file list
            current_site = Site.objects.get_current()
                        
            # read esgf_cogs.xml 
            with open (self.filepath, "r") as myfile:
                
                xml=myfile.read().replace('\n', '')
    
                # <sites>
                root = fromstring(xml)
                
                # update/insert all sites found in file
                domains = [] # list of site domains found in file
                for site in root.findall("site"):
                    name = site.attrib['name']
                    domain = site.attrib['domain']
                    domains.append(domain)
                    log.debug('Updating site domain: %s name: %s' % (domain, name))
                    
                    # update Site objects
                    try:
                        _site = Site.objects.get(domain=domain)
                        if _site != current_site:
                            # update site
                            _site.name = name
                            _site.save()
                            log.debug('Updated site: %s' % _site)
                    except ObjectDoesNotExist:
                        _site = Site.objects.create(name=name, domain=domain)
                        log.debug('Created site: %s' % _site)
                        
                    # update PeerSite objects
                    try:
                        peersite = PeerSite.objects.get(site=_site)
                    except ObjectDoesNotExist:
                        peersite = PeerSite.objects.create(site=_site, enabled=False)
                    log.debug('\tPeer site: %s' % peersite)
                            
            # clean up stale sites
            if delete:
                for peer in PeerSite.objects.all():
                    if peer.site.domain not in domains:
                        if peer.site != current_site:
                            log.warning('Stale peer site found at domain: %s' % peer.site.domain + ", deleting it...")
                            peer.site.delete() # will also delete the PeerSite object on cascade

        else:
            log.warning('File %s does not exist, skipping update of ESGF peer nodes' % self.filepath)