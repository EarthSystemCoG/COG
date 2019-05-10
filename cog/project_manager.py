'''
Class responsible for listing and serving federation-wide projects.
'''

from django.contrib.sites.models import Site
from cog.models import Project, ProjectTag, deleteProject
from cog.utils import getJson, str2bool

from cog.models import getPeerSites
from distutils.util import strtobool

import logging

log = logging.getLogger(__name__)

class ProjectManager(object):
  
    def sync(self):
        '''Updates the list of remote projects from all peer sites.'''
        
        # loop over peer sites  
        sites = {}  
        totalNumberOfProjects = 0
        totalNumberOfUsers = 0   
        
        # loop over federated peer site + local site
        allSites = getPeerSites()
        local_site = Site.objects.get_current()
        allSites.append( local_site )
        for site in allSites:
            url = "http://%s/share/projects/" % site.domain
            numberOfUsers = 0
            numberOfProjects = 0
            jobj = getJson(url)
            if jobj is None:
                status = 'ERROR'
            else:
                status = 'OK'
                numberOfProjects = len( jobj["projects"])
                numberOfUsers = int( jobj.get("users",0) )
                if site != local_site:
                    # harvest projects, tags from remote site
                    self._harvest(jobj)
                    
            sites[site.id] = { 'name': site.name, 'domain':site.domain, 'url': url, 'status':status,
                               'numberOfProjects': numberOfProjects, 'numberOfUsers': numberOfUsers  }
            
            totalNumberOfProjects += numberOfProjects
            totalNumberOfUsers += numberOfUsers
            
        return sites, totalNumberOfProjects, totalNumberOfUsers
        
    def _associateProjects(self, objList, apDictList):
        
        # empty list of parents/peers/children
        objList.clear()
        for apdict in apDictList:
            short_name=apdict['short_name']
            site_domain=apdict['site_domain']
            try:
                aproject = Project.objects.get(short_name=short_name, 
                                               site__domain=site_domain)
                objList.add(aproject)
            except Project.DoesNotExist: # correct short name, wrong site ?
                log.error('Associated project does not exist in local database: short_name=%s site_domain=%s, will ignore' % (apdict['short_name'], apdict['site_domain']))
                pass 
                    
        
    def _harvest(self, jobj):
        '''
        Parses a JSON document obtained from a remote CoG instance.
        Also removes obsolete projects from that remote site.
        '''
        
        # use current site to prevent overriding local objects
        local_site = Site.objects.get_current()
                    
        # load/create remote site by domain
        sdict = jobj["site"]
        
        # DO NOT OVERRIDE LOCAL OBJECTS
        if sdict['domain'] != local_site.domain: 
            
            remote_site, created = Site.objects.get_or_create(domain=sdict['domain'])
            if created:
                log.debug('Created remote site: %s' % remote_site)
            else:
                log.debug('Remote site %s already existing' % remote_site)
            #remote_site.name = sdict["name"] # don't change the site 'name', keep value from esgf_cogs.xml instead
            #remote_site.save()
                        
            # first loop to create ALL projects first
            for key, pdict in jobj["projects"].items():
                              
                short_name = pdict['short_name']
                long_name = pdict['long_name']
                site_domain = pdict['site_domain']
                
                # check site
                if site_domain==remote_site.domain: # check project belongs to remote site
                    
                    if not Project.objects.filter(short_name__iexact=short_name).exists(): # avoid conflicts with existing projects, from ANY site
                        # create new project
                        log.debug('Creating project=%s (%s) for site=%s in local database' % (short_name, long_name, remote_site))
                        try:
                            Project.objects.create(short_name=short_name, long_name=long_name, site=remote_site, active=True)
                            log.debug('Created project=%s for site=%s in local database' % (short_name, remote_site))
                        except Exception as e:
                            log.error(str(e)) # ignore errors while creating any one project from remote site, continue iteration
                    else:
                        log.debug('Project with name:%s already exists (local or remote)' % short_name)
            
            # second loop to update project attributes and associations
            for key, pdict in jobj["projects"].items():
                
                short_name = pdict['short_name']
                long_name = pdict['long_name']
                site_domain = pdict['site_domain']
                private = pdict.get('private', 'False')
                shared = pdict.get('shared', 'True')
                
                # check site
                if site_domain==remote_site.domain: # check project belongs to remote site
                
                    try:
                        # load existing project from remote site
                        project = Project.objects.get(short_name=short_name, site=remote_site)
                        log.debug('Loaded project: %s from site: %s' % (short_name, site_domain))
                        
                        # update project attributes
                        project.long_name = long_name
                        
                        # public/private
                        project.private = strtobool(private)
                            
                        # shared/local
                        project.shared = strtobool(shared)
                                                
                        # update project tags
                        project.tags.clear()
                        for tagname in pdict['tags']:
                            ptag, created = ProjectTag.objects.get_or_create(name=tagname)
                            project.tags.add(ptag)
                        
                        # update project associations
                        self._associateProjects(project.peers, pdict['peers'])
                        log.debug('Updated project peers=%s' % project.peers.all())
                        self._associateProjects(project.parents, pdict['parents'])
                        log.debug('Updated project parents=%s' % project.parents.all())
                        
                        project.save()
                        
                    except Project.DoesNotExist:
                        pass # correct name, wrong site
                    
            # remove obsolete projects from this remote site
            for proj in Project.objects.filter(site=remote_site):
                if proj.short_name not in jobj["projects"]:
                    # delete the project and associated objects
                    deleteProject(proj, dryrun=False, rmdir=False) # no local site media directory for remote project

            # remove unused tags
            for tag in ProjectTag.objects.all():
                if len(tag.projects.all()) == 0:
                    tag.delete()    
        
    def listAllProjects(self):
        '''List all projects.'''
                    
        return Project.objects.filter(active=True).order_by('short_name')
    
    def listAssociatedProjects(self, project, ptype):
        
        if ptype=='parents':
            return project.parents.all()
            
        elif ptype=='peers':
            return project.peers.all()
            
        elif ptype=='children':
            return project.children()
            
        else:
            return []
        
projectManager = ProjectManager()
