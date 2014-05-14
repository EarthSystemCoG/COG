'''
Class responsible for listing and serving federation-wide projects.
'''

from django.contrib.sites.models import Site
from cog.models import Project, ProjectTag
import urllib2
import json

TIMEOUT = 5

class ProjectManager(object):
    '''
    def __init__(self):
        
        # dictionary of dictionaries holding all projects in the federation
        # self._projects[site.domain][project.short_name] = <project object>
        self._projects = {}
        
        print 'Initializing project manager with local projects'
        site = Site.objects.get_current()
        self._projects[site.domain] = {}
        for project in Project.objects.filter(active=True): # FIXME ?
            self._projects[site.domain][project.short_name] = project
    '''     

    def _reload(self):
        
        self._listRemoteProjects("http://localhost:8000/share/projects/")
        
        
    def _listRemoteProjects(self, url):
        
        try:
            opener = urllib2.build_opener()
            request = urllib2.Request(url)
            response = opener.open(request, timeout=TIMEOUT)
            jdoc = response.read()
            jobj = json.loads(jdoc)
            
            for pdict in jobj["projects"]:
                print "\nproject=%s" % pdict
                
                # create minimal project
                proj = Project(short_name=pdict['short_name'], 
                               long_name=pdict['long_name'],
                               description='-')
                
                # associate tags
                #tags = []
                #for tag in pdict['tags']:
                #    proj.tags.append(ProjectTag(name=tag))
                
                #print proj
                #print proj.tags
            
        except Exception as e:
            print 'Error retrieving url=%s' % url
            print e
        
    def listAllProjects(self):
        '''List all projects.'''
                
        #projects = []
        #for site in self._projects.keys():
        #    projects = projects + self._projects[site].values()
        #return sorted(projects, key=lambda proj: proj.short_name) 
    
        return Project.objects.filter(active=True).order_by('short_name')
    
    def listAssociatedProjects(self, project, ptype):
        
        if ptype=='parents':
            return project.parents.all()
            
        elif ptype=='peers':
            return project.peers.all()
            
        elif ptype=='child':
            return project.children()
            
        else:
            return []
        
projectManager = ProjectManager()
