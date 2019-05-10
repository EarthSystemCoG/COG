from django.db import models
import ConfigParser
from datetime import datetime
import os
import logging

INVALID_CHARACTERS = ['>','<','&','$','!','\\','\/','\'','\"','(',')','[',']','{','}']

ERROR_MESSAGE_INVALID_TEXT = "Error: search query text cannot contain any of the characters: %s" % INVALID_CHARACTERS
ERROR_MESSAGE_INVALID_DATE = 'Max/Min Version dates must be of the format: YYYYMMDD'

# maximum number of results per page
LIMIT = 10

log = logging.getLogger(__name__)

class Facet:
    def __init__(self, key, label):
        self.key = key
        self.label = label
        self.values = {} # (value, counts)
        
    # method hides the internal storage of values
    def addValue(self, value, counts=0):
        self.values[value] = counts
        
    def addCount(self, value):
        try:
            self.values[value] = self.values[value] + 1
        except KeyError:
            self.values[value] = 0
        
    def getValues(self):
        return self.values
    
    def getSortedValues(self):
        '''Returns list of (value, counts) tuples sorted by value.'''
        return [(value, self.values[value]) for value in sorted(self.values.keys())]
        
    def printme(self):
        log.debug("Facet: key=%s label=%s" % (self.key, self.label))
        for value, counts in self.values.items():
            log.debug("Value=%s counts=%d" % (value, counts))
            
class SearchInput:
    
    def __init__(self):
        self.offset = 0
        self.limit = LIMIT
        self.constraints = {}
        self.query = ''
        self.type = 'Dataset' # default target type
        self.replica = False
        self.latest = True
        self.local = False
        self.max_version = ''
        self.min_version = ''
        
    def addConstraint(self, name, value):
        try:
            self.constraints[name].append(value)
        except KeyError:
            self.constraints[name] = [value]
        log.debug("Added constraint name=%s value(s)=%s" % (name, self.constraints[name]))
        
    def setConstraint(self, name, values):
        self.constraints[name] = values
        
    def hasConstraint(self, name):
        return name in self.constraints
    
    def getConstraint(self, name):
        return self.constraints.get(name, None)
        
    def isValid(self):
        
        # validate query text
        for c in INVALID_CHARACTERS:
            if c in self.query:
                return (False, ERROR_MESSAGE_INVALID_TEXT)
        
        # validate max/min version dates
        if self.max_version:
            try:
                datetime.strptime( self.max_version, "%Y%M%d" )
            except ValueError:
                return (False, ERROR_MESSAGE_INVALID_DATE)
        if self.min_version:
            try:
                datetime.strptime( self.min_version, "%Y%M%d" )
            except ValueError:
                return (False, ERROR_MESSAGE_INVALID_DATE)

            
        return (True, '')
    
    def isMaxVersionDateValid(self):
        return False
    
    def isEmpty(self):
        return self.query == '' and len(self.constraints)==0
        
    def printme(self):
        log.debug(
            "Search Input: Query=%s Type=%s Offset=%d Limit=%d Max Version=%s Min Version=%s" % (
                self.query, self.type, self.offset, self.limit, 
                self.max_version, self.min_version
            )
        )
        for key, values in self.constraints.items():
            log.debug("Constraint: key=%s value(s)=%s" % (key, values))
        
        
class SearchOutput:
    
    def __init__(self):
        self.results = []
        self.facets = {} # (facet key, facet)
        self.counts = 0
        
    def setFacet(self, facet):
        self.facets[facet.key] = facet
        
    def printme(self):
        log.debug("Search Output: Total number of results=%d" % self.counts)
        for facet in self.facets.values():
            facet.printme()
        for record in self.results:
            record.printme()
        
            
class Record:
    
    def __init__(self, id):
        self.id = id
        self.fields = {}
        
    def addField(self, name, value):
        try:
            self.fields[name].append(value)
        except KeyError:
            self.fields[name] = [value]
            
    def printme(self):
        log.debug("Record id=%s" % self.id)
        for name, values in self.fields.items():
            log.debug("Field name=%s values=%s" % (name, values))
                        
class FacetProfile:
    
    """
    Class representing an ordered list of facet keys and labels to be used in the faceted search interface.
    An instance is initialized with a list of facet groups, 
    where each facet group is a list of tuples of the form: [ (facet1_key, facet1_label),...(facetN_key, facetN_label)]
    """
    def __init__(self, facetGroups):
        
        self.facetGroups = facetGroups
        
        # merge all dictionaries, keys
        self.keys = []
        self.map = {}
        for group in self.facetGroups:
            self.keys = self.keys + group.keys
            self.map = dict( self.map.items() + group.map.items() )
                        
    def getAllKeys(self):
        """Returns a list of keys over all its facet groups."""
        return self.keys
    
    def getLabel(self, key):
        '''Returns the facet label for the given key, or None if the key is not found.'''
        return self.map.get(key, None)
    
class FacetGroup:
    """
    Class representing an ordered list of facet keys and labels to be used in the faceted search interface.
    An instance is initialized with a list of tuples of the form: [ (facet1_key, facet1_label),...(facetN_key, facetN_label)],
    and an optional name representing the group.
    """
    
    def __init__(self, facets, name=None):
        self.facets = facets
        self.name = name
        
        # build dictionary for quick lookup of facet label by facet key
        self.map = {}
        for tuple in facets:
            self.map[tuple[0]] = tuple[1]
            
        # ordered set of facet keys
        self.keys = [ tuple[0] for tuple in self.facets ]
        
    # this method returns an ORDERED set of facet keys 
    def getKeys(self):
        return self.keys
    
    # this method will raise a KeyError if the key is not found
    def getLabel(self, key):
        return self.map[key]

        
class SearchConfig:
    """
    Class containing parameters to configure a search service.
    """
    
    def __init__(self, facetProfile, fixedConstraints, searchService,
                 replicaFlag, latestFlag, localFlag):
        
        # back-end search service
        self.searchService = searchService
        
        # object containing facets displayed user interface
        self.facetProfile = facetProfile
        
        # map of (name,values[]) constraints to be always added to the search
        self.fixedConstraints = fixedConstraints
        
        # option check-boxes
        self.replicaFlag = replicaFlag
        self.latestFlag = latestFlag
        self.localFlag = localFlag
        
    def printme(self):
        log.debug('Search Configuration Service:%s' % self.searchService)
        log.debug('Search Configuration Facets:')
        for facetGroup in self.facetProfile.facetGroups:
            log.debug("Facet Group=%s" % facetGroup.name)
            for key in facetGroup.getKeys():
                log.debug("\t\tFacet key=%s, label=%s" % (key, facetGroup.getLabel(key)))
        log.debug('Search Configuration Fixed Constraints=%s' % self.fixedConstraints)
        log.debug(
            'Search Configuration options: show replica checkbox: %s, show latest checkbox: %s, show local checkbox:%s' % (
                self.replicaFlag, self.latestFlag, self.localFlag
            )
        )
    
class SearchMappings(object):
    """Class that reads facet option mappings from a local configuration file,
       and stores them in memory for faster access.
       Note that currently mappings are application-scope. """
    
    def __init__(self):
        
        cog_config_dir = os.getenv('COG_CONFIG_DIR', '/usr/local/cog/cog_config')
        CONFIGFILEPATH = os.path.join(cog_config_dir, 'cog_search.cfg')
        
        self.mappings = {}
        config = ConfigParser.RawConfigParser()
        try:
            config.read( CONFIGFILEPATH )
            for facet_key in config.sections():
                fmap = {}
                for facet_option in config.options(facet_key):
                    facet_label = config.get(facet_key, facet_option)
                    fmap[facet_option]=facet_label
                    # log.debug("Facet=%s mapping key=%s to value=%s" % (facet_key, facet_option, facet_label))
                self.mappings[facet_key] = fmap
            # log.debug('Loaded search mappings from file: %s' % filepath)
        except Exception as e:
            log.debug("Search mappings file not found %s" % str(e))
            
    def getFacetOptionLabel(self, facet_key, facet_option):
        """Returns the facet_option for the given facet_key if found,
           otherwise it returns facet_option.
           Note that facet keys and options are reduced to lower case before mapping."""
        if self.mappings.get(facet_key.lower(), None) is not None:
            return self.mappings[facet_key.lower()].get(facet_option.lower(), facet_option)
        else:
            return facet_option
            
    
# global mappings object
searchMappings = SearchMappings()