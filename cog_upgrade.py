# Python script to upgrade the content of an existing COG installation
import sys, os, ConfigParser

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.models import Project, create_upload_directory, Doc, CommunicationMeans
from cog.models.logged_event import log_instance_event
from django.db.models.signals import post_save
from cog.models import SearchFacet, SearchProfile, SearchGroup

print 'Upgrading COG'

# 0.9 release

#for project in Project.objects.all():
#    create_upload_directory(project)
    
# assign is_private=False to all documents
# must first disconnect the signal sent when saving a Doc object (to avoid spurious signals for all Docs)
#post_save.disconnect(log_instance_event, sender=Doc, dispatch_uid="log_doc_event")
#for doc in Doc.objects.all():
#    print 'doc=%s' % doc
#    if not doc.is_private:
#        # explicitly assign
#        doc.is_private = False
#        doc.save()
#    doc.path = doc.file.name
#    doc.save()
 
 
# 1.0 release
#for cm in CommunicationMeans.objects.all():
#    print "Communication Means: title=%s internal=%s" % (cm.title, cm.internal)   
#    cm.internal=True
#    cm.save()
#    print "Communication Means: title=%s internal=%s" % (cm.title, cm.internal) 
    
# 1.6 release
# delete existing facets
for f in SearchFacet.objects.all():
    print f
    f.delete()
    
# read search configurations
configs = { 'NCPP': 'cog/config/search/ncpp.cfg',
            'Downscaling-2013': 'cog/config/search/ncpp.cfg',
            'DCMIP-2012': 'cog/config/search/dcmip-2012.cfg' }

for key in configs:
    
    # load project search profile
    project = Project.objects.get(short_name=key)
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
        projConfig.read( os.path.expanduser(configs[key]) )
    except Exception as e:
        print "Configuration file %s not found" % CONFIG_FILEPATH
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