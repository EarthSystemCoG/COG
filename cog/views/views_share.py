'''
Views for exchanging information with other sites.
'''
from django.http import HttpResponseNotAllowed, HttpResponse
import json
from cog.models import Project
from django.contrib.sites.models import Site

JSON = "application/json"

def serialize_project(project):
    
    # this project
    pdict = { 'short_name': project.short_name,
              'long_name': project.long_name,
              'site': project.site.id }
    
    # associated projects
    pdict["parents"] = _serialize_associated_projects( project.parents.all() )
    pdict["peers"]   = _serialize_associated_projects( project.peers.all() )
    pdict["children"] = _serialize_associated_projects( project.children() )
    
    # tags
    tags = []
    for tag in project.tags.all():
        tags.append( tag.name )
    pdict["tags"] = tags
    
    return pdict

def _serialize_associated_projects( projects ):
    
    plist = []
    for project in projects:
        plist.append( {'short_name': project.short_name,
                       'site_domain': project.site.domain } )
    return plist

def serialize_site(site):
    
    sdict = { 'domain': site.domain,
              'name': site.name }
    
    return sdict

# real view
def share_projects(request):
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # list sites
        sites = []
        for site in Site.objects.all():
            sites.append( serialize_site(site) )
        response_data['sites'] = sites
        
        # list projects from this site
        current_site = Site.objects.get_current()
        projects = []
        print 'Listing active, public projects for site=%s' % current_site
        for project in Project.objects.filter(active=True).filter(private=False).filter(site=current_site):
            projects.append( serialize_project(project) )
            
        response_data["projects"] = projects   
        
        return HttpResponse(json.dumps(response_data), content_type=JSON)
    else:
        return HttpResponseNotAllowed(['GET'])

# fake view
'''
def share_projects(request):
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # list sites
        site = Site(domain="jpl.nasa.gov", name="http://jpl.nasa.gov/")
        sites = [ serialize_site(site)  ]
        response_data['sites'] = sites
        
        proj1 = Project(short_name='Proj1', long_name='Project #1', description='This is project #1')
        proj2 = Project(short_name='Proj2', long_name='Project #2', description='This is project #2')
        projects = [ serialize_project(proj1),
                     serialize_project(proj2) ]
                    
        response_data["projects"] = projects   
        
        return HttpResponse(json.dumps(response_data), content_type=JSON)
    else:
        return HttpResponseNotAllowed(['GET'])
'''
