'''
Views for exchanging information with other sites.
'''
from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden
import json
from cog.models import Project
from django.contrib.sites.models import Site
from cog.project_manager import projectManager
from cog.views.constants import PERMISSION_DENIED_MESSAGE

JSON = "application/json"

def serialize_project(project):
    
    # this project
    pdict = { 'short_name': project.short_name,
              'long_name': project.long_name,
              'site_domain': project.site.domain }
    
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

def share_projects(request):
    '''Exposes the site's projects as a JSON-formatted list.'''
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # list sites
        current_site = Site.objects.get_current()
        response_data['site'] = serialize_site(current_site)
        
        # list projects from this site
        current_site = Site.objects.get_current()
        projects = {}
        print 'Listing active, public projects for current site=%s' % current_site
        for project in Project.objects.filter(active=True).filter(private=False).filter(site=current_site):
            projects[project.short_name] = serialize_project(project)
            
        response_data["projects"] = projects   
        
        return HttpResponse(json.dumps(response_data, indent=4), content_type=JSON)
    else:
        return HttpResponseNotAllowed(['GET'])
    
def share_reload(request):
    '''Updates the list of remote projects in current database.'''
    
    if not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    sites = projectManager.reload()
    
    return HttpResponse(json.dumps(sites), content_type=JSON)
    
    