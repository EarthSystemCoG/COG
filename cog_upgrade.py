# Python script to upgrade the content of an existing COG installation
import sys, os

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.models import Project, create_upload_directory

print 'Upgrading COG'

for project in Project.objects.all():
    create_upload_directory(project)