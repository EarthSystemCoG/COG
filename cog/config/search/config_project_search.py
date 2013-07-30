import sys, os, ConfigParser
from cog.models import Project, SearchGroup, SearchFacet

def config_project_search(project_short_name, config_file_path):
    
    # load project search profile
    project = Project.objects.get(short_name=project_short_name)
    search_profile = project.searchprofile
    
    # remove existing groups of facets
    for group in search_profile.groups.all():
        print 'Deleting search group=%s' % group
        group.delete()
    
    # read project configuration
    projConfig = ConfigParser.RawConfigParser()
    # must set following line explicitely to preserve the case of configuration keys
    projConfig.optionxform = str 
    try:
        projConfig.read( os.path.expanduser(config_file_path) )
    except Exception as e:
        print "Configuration file %s not found" % config_file_path
        raise e
    
    # loop over groups
    for section in projConfig.sections():
        
        # create search group
        parts = section.split("=")
        group_order = parts[0]
        group_name=parts[1]
        searchGroup = SearchGroup(name=group_name, order=int(group_order), profile=search_profile)
        searchGroup.save()

        for option in projConfig.options(section):
            value = projConfig.get(section, option)
            #print section, option, value
            parts = value.split("|")
            facet_order = int(option)
            facet_key = parts[0]
            facet_label = parts[1]
            searchFacet = SearchFacet(group=searchGroup, key=facet_key, order=facet_order, label=facet_label)
            searchFacet.save()
            print "%s" % searchFacet