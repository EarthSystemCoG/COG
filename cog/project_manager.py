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

    def reload(self):
        
        self._listRemoteProjects("http://localhost:8001/share/projects/")
        
    def _associateProjects(self, objList, apDictList):
        
        # empty list of parents/peers/children
        objList.clear()
        print apDictList
        for apdict in apDictList:
            short_name=apdict['short_name']
            site_domain=apdict['site_domain']
            print 'Trying short_name=%s site_domain=%s' % (short_name, site_domain)
            try:
                aproject = Project.objects.get(short_name=short_name, 
                                               site__domain=site_domain)
                objList.add(aproject)
            except Project.DoesNotExist: # correct short name, wrong site ?
                print 'does not exist %s %s' % (apdict['short_name'], apdict['site_domain'])
                pass 

        print objList.all()
        
    def _listRemoteProjects(self, url):
        
        try:
            opener = urllib2.build_opener()
            request = urllib2.Request(url)
            response = opener.open(request, timeout=TIMEOUT)
            jdoc = response.read()
            jobj = json.loads(jdoc)
            
            # create sites
            for sdict in jobj['sites']:
                site, created = Site.objects.get_or_create(domain=sdict['domain'], name=sdict['name'])
                if created:
                    print 'Created federated site: %s' % site
                else:
                    print 'Site %s already existing' % site
            
            # first loop to create ALL projects
            for pdict in jobj["projects"]:                
                short_name = pdict['short_name']
                long_name = pdict['long_name']
                site_domain = pdict['site_domain']
                
                if Project.objects.filter(short_name=short_name).exists(): # NOTE: check existence independent of site
                    print 'Project=%s already exists in the local database' % short_name
                    
                else:
                    
                    try:
                        site = Site.objects.get(domain=site_domain)
                        Project.objects.create(short_name=short_name, long_name=long_name, description='-', site=site, active=True)
                        print 'Created project=%s site=%s in local database' % (short_name, site)
                        
                    except Site.DoesNotExist:
                        print 'Warning: project=%s has invalid site=%s, will not create' % (short_name, site_domain)
                
            # second loop to update project attributes
            for pdict in jobj["projects"]:
                
                short_name = pdict['short_name']
                long_name = pdict['long_name']
                site_domain = pdict['site_domain']
                
                try:
                    project = Project.objects.get(short_name=short_name, site__domain=site_domain)
                    print 'Loaded project=%s' % project
                    
                    # update project attributes
                    project.long_name = long_name
                    
                    # update project tags
                    project.tags.clear()
                    for tagname in pdict['tags']:
                        print 'loading tag=%s' % tagname
                        ptag, created = ProjectTag.objects.get_or_create(name=tagname)
                        print 'tag=%s' % ptag
                        project.tags.add(ptag)
                    
                    # update project associations
                    self._associateProjects(project.peers, pdict['peers'])
                    print 'Updated project peers=%s' % project.peers.all()
                    self._associateProjects(project.parents, pdict['parents'])
                    print 'Updated project parents=%s' % project.parents.all()
                    print pdict['parents']

                        
                    
                    project.save()
                    
                except Project.DoesNotExist:
                    pass # correct name, wrong site

            # remove unused tags
            for tag in ProjectTag.objects.all():
                if len(tag.projects.all()) == 0:
                    tag.delete()

                
                
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
