import sys, os, ConfigParser
import logging

from django.conf import settings
from cog.models import Project, SearchGroup, SearchFacet
from cog.utils import str2bool

SECTION_GLOBAL = 'GLOBAL'

log = logging.getLogger(__name__)

class SearchConfigParser():
    '''Class that enables import/export of project search configuration to local Python configuration files.'''
    
    def __init__(self, project):
        self.project = project
        self.config_file_path = '%s/%s/search.cfg' % (settings.PROJECT_CONFIG_DIR, project.short_name.lower())
        
    def _getConfigParser(self):
        
        # read project configuration
        configParser = ConfigParser.RawConfigParser()
        # must set following line explicitly to preserve the case of configuration keys
        configParser.optionxform = str 
        
        return configParser


    def write(self):
        '''Writes the project search configuration to the file $COG_CONFIG_DIR/projects/<project_short_name>/search.cfg'''
        
        log.debug('Writing search configuration for project=%s' % self.project.short_name)
        
        # load project search profile
        project = Project.objects.get(short_name=self.project.short_name)
        search_profile = project.searchprofile
        
        # create directory if not existing already
        (filepath, filename) = os.path.split(self.config_file_path)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        
        # write project configuration
        projConfig = self._getConfigParser()
        
        # GLOBAL SECTION
        projConfig.add_section(SECTION_GLOBAL)
        projConfig.set(SECTION_GLOBAL, 'url', search_profile.url)
        projConfig.set(SECTION_GLOBAL, 'constraints', search_profile.constraints)
        projConfig.set(SECTION_GLOBAL, 'modelMetadataFlag', search_profile.modelMetadataFlag)
        projConfig.set(SECTION_GLOBAL, 'replicaSearchFlag', search_profile.replicaSearchFlag)
        projConfig.set(SECTION_GLOBAL, 'latestSearchFlag', search_profile.latestSearchFlag)
        projConfig.set(SECTION_GLOBAL, 'localSearchFlag', search_profile.localSearchFlag)
        
        # FACET GROUP SECTIONS
        for group in search_profile.groups.all().order_by('order'):
            section = "%s=%s" % (group.order, group.name)
            projConfig.add_section(section)
            
            for facet in SearchFacet.objects.filter(group=group).order_by('order'):
                key=facet.order
                value = "%s|%s" % (facet.key, facet.label) 
                projConfig.set(section, key, value)
        
        with open(self.config_file_path,'w') as config_file:
            projConfig.write(config_file)


    
    def read(self):
        '''Reads the project search configuration from the file $COG_CONFIG_DIR/projects/<project_short_name>/search.cfg'''
        
        log.debug('Reading search configuration for project=%s' % self.project.short_name)
        
        # load project search profile
        project = Project.objects.get(short_name=self.project.short_name)
        search_profile = project.searchprofile
        
        # remove existing groups of facets
        for group in search_profile.groups.all():
            log.debug('Deleting search group=%s' % group)
            group.delete()
        
        # read project configuration
        projConfig = self._getConfigParser()
        try:
            projConfig.read( self.config_file_path )
        except Exception as e:
            log.error("Configuration file %s not found" % self.config_file_path)
            raise e
        
        # loop over configuration sections
        for section in projConfig.sections():
                        
            # global search configuration
            if section==SECTION_GLOBAL:
                for key in ['url', 'constraints', 'modelMetadataFlag', 'replicaSearchFlag', 'latestSearchFlag', 'localSearchFlag']:
                    if projConfig.has_option(section, key):
                        if key in ['modelMetadataFlag', 'replicaSearchFlag', 'latestSearchFlag', 'localSearchFlag']:
                            value = str2bool( projConfig.get(section, key) ) # must convert string value to boolean
                        else:
                            value = projConfig.get(section, key)
                        setattr(search_profile, key, value)
                search_profile.save()
                
            # facet configuration
            else:
                # create search group
                parts = section.split("=")
                group_order = parts[0]
                group_name=parts[1]
                searchGroup = SearchGroup(name=group_name, order=int(group_order), profile=search_profile)
                searchGroup.save()
        
                for option in projConfig.options(section):
                    value = projConfig.get(section, option)
                    log.debug("Section: %s, Option: %s, Value: %s" % (section, option, value))
                    parts = value.split("|")
                    facet_order = int(option)
                    facet_key = parts[0]
                    facet_label = parts[1]
                    searchFacet = SearchFacet(group=searchGroup, key=facet_key, order=facet_order, label=facet_label)
                    searchFacet.save()
            
if __name__ == '__main__':
    
    sys.path.append( os.path.abspath(os.path.dirname('.')) )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    
    project_short_name = sys.argv[1]
    
    project = Project.objects.get(short_name=project_short_name)
    parser = SearchConfigParser(project)
    parser.read()
    