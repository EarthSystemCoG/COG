# Example script to create a hierarchy of projects.
# All projects at the same level are marked as peers.
import os, sys
sys.path.append( os.path.abspath(os.path.dirname('../.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'COG.settings'

import cog
from cog.models import *
from cog.utils import *
from django.core.exceptions import ObjectDoesNotExist

projects = { 
            'NESII|NOAA Environmental Software Infrastructure and Interoperability' : 
            { 
             'ESMF|Earth System Modeling Framework' : 
             {
              'ESMF-NUOPC|ESMF for NUOPC' : {},
              'ESMF-Atts|ESMF Attributes' : {},
              'ESMF-CCSM|ESMF in CCSM' : {},
              'ESMF-WS|ESMF Web Services' : {},
             }, 
             'Curator|Curator Classic' : {
                                          'Curator-Obs|Curator for Observations' : {},
                                          },
             'Curator-Hydro|Curator Hydro' : {},
             'COG|Commodity Governance' : {},
             'NCPP|National Climate Prediction Portal' : {},
             'GIP|Global Interoperability Program' : {}, 
            },
           }

peers = { 
         'ESMF-NUOPC' : ['ESMF-Atts'],
         'ESMF-Atts' : ['ESMF-CCSM'],
         'ESMF-CCSM' : ['Curator'],
         'Curator-Hydro' : ['Curator','ESMF-WS'],
         'COG' : ['NCPP','GIP','Curator'],
         'GIP' : ['NCPP'],
         }
    
def create_project(key, children, parent, peers):
    
    # create this project if not existing
    proj_names = key.split('|')
    try :
        p = Project.objects.all().get(short_name=proj_names[0])
    except ObjectDoesNotExist :
        p = Project.objects.create(short_name=proj_names[0], long_name=proj_names[1], description='%s description' % proj_names[1])
        # set parent
        if parent:
            p.parent = parent
        p.save()
    p = Project.objects.all().get(short_name=proj_names[0])
    
    # create project home page
    admin = User.objects.get(username='admin')
    if not p.isInitialized():
        create_project_home(p, admin)
        
    # recursion
    for child in children.keys():
        # NOTE: define siblings to be peers
        create_project(child, children[child], p, p.children() )
    
    return p
        
# create all projects       
for key in projects.keys():
    proj = create_project(key, projects[key], None, peers)
    
# set all peers
for key in peers.keys():
    project = Project.objects.all().get(short_name=key)
    for value in peers[key]:
        peer = Project.objects.all().get(short_name=value)
        project.peers.add(peer)
    project.save()

# print out all projects
for p in Project.objects.all():
    print 'Project %s' % p
    print '\t parent: %s' % p.parent
    for pp in p.children():
        print '\t child: %s' % pp
    for pp in p.peers.all():
        print '\t peer: %s' % pp
        
def add_news_to_children(project, news):
    for child in project.children():
        news.other_projects.add(child)
        add_news_to_children(child, news)
def add_news_to_peers(project, news):
    for peer in project.peers.all():
        news.other_projects.add(peer)
        add_news_to_children(peer, news)
        
# attach some news
#for p in Project.objects.all():
#    news_title = "Breaking News for Project %s" % p.short_name
#    author = User.objects.get(username='admin')
#    try :
#        news = News.objects.all().get(title=news_title)
#    except ObjectDoesNotExist :
#        news = News.objects.create(title=news_title, 
#                                   text='The US government dramatically increased the budget of project %s after the number of news increased from %i' \
#                                   % (p.short_name, len(p.news())),
#                                   author = author, project=p)
#        # propagate to children
#        add_news_to_children(p, news)
#        # propagate news to peers
#        add_news_to_peers(p, news)
#        news.save()
        
for p in Project.objects.all():
    print "Project: %s" % p.full_name()
    for news in p.news():
        print "\t %s" % news