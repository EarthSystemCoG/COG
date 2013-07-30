# Python script to upgrade the content of an existing COG installation
import sys, os, ConfigParser

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.models import Project, create_upload_directory, Doc, CommunicationMeans
from cog.models.logged_event import log_instance_event
from django.db.models.signals import post_save
from cog.models import SearchFacet, SearchProfile, SearchGroup
from cog.config.search import config_project_search

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
    config_project_search(key, configs[key])