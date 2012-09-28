# Python script to upgrade the content of an existing COG installation
import sys, os

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.models import Project, create_upload_directory, Doc
from cog.models.logged_event import log_instance_event
from django.db.models.signals import post_save

print 'Upgrading COG'

for project in Project.objects.all():
    create_upload_directory(project)
    
# assign is_private=False to all documents
# must first disconnect the signal sent when saving a Doc object (to avoid spurious signals for all Docs)
post_save.disconnect(log_instance_event, sender=Doc, dispatch_uid="log_doc_event")
for doc in Doc.objects.all():
    print 'doc=%s' % doc
    if not doc.is_private:
        # explicitly assign
        doc.is_private = False
        doc.save()
    doc.path = doc.file.name
    doc.save()
    