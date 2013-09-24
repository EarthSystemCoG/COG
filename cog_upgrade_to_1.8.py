# Python script to upgrade the content of an existing COG installation
import sys, os, ConfigParser

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.models import *
from cog.models.logged_event import log_instance_event
from django.db.models.signals import post_save
from cog.models import SearchFacet, SearchProfile, SearchGroup, Folder
from cog.config.search import config_project_search
from django.conf import settings
from cog.models.utils import create_project_search_profile, get_or_create_default_search_group
from django.core.exceptions import ObjectDoesNotExist

print 'Upgrading COG to version 1.7'

# loop over projects, folders
for project in Project.objects.all():
    
    folders = Folder.objects.filter(project=project)
    
    # set all current folder state to active=True
    # rename top-level folder
    for folder in folders:
        folder.active = True
        if folder.name == '%s %s' % (project.short_name, TOP_FOLDER):
            folder.name = TOP_FOLDER 
        folder.save()
        
    # create all other pre-defined folders, in the proper order
    topFolder = getTopFolder(project)
    order = 0
    for key, value in TOP_SUB_FOLDERS.items():
        order += 1
        folder, created = Folder.objects.get_or_create(name=value, project=project)
        folder.parent = topFolder
        folder.order = order
        if created:  
            print 'Project=%s: created top-level folder=%s' % (project.short_name, folder.name)
            folder.active=False
        else:
            folder.active = True
        folder.save()
            

# rename tabs
for project in Project.objects.all():
    for tab in ProjectTab.objects.filter(project=project):
        if tab.label == 'Communication':
            tab.label = 'Communications'
            tab.save()
            print 'Renamed tab %s to: Communications' % tab
        elif tab.label == 'Roadmap':
            tab.label = 'Roadmaps'
            tab.save()
            print 'Renamed tab %s to: Roadmaps' % tab
                
# remove obsolete pages
oldpages = ['getinvolved','code','support']
for project in Project.objects.all():
    posts = Post.objects.filter(project=project)
    for post in posts:
        for oldpage in oldpages:
            url = "/projects/%s/%s/" % (project.short_name.lower(), oldpage)
            if post.url==url or post.url == url[0:-1]:
                print 'Deleting page: %s' % post.url
                post.delete()