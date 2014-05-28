'''
Views for exchanging information with other sites.
'''
from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
import json
from cog.models import Project, getProjectsForUser
from django.contrib.sites.models import Site
from cog.project_manager import projectManager
from cog.views.constants import PERMISSION_DENIED_MESSAGE
from django_openid_auth.models import UserOpenID

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

def serialize_user(user):
    
    udict = { 'openid': user.profile.openid(),
              'site_name': user.profile.site.name,
              'site_domain': user.profile.site.domain }
    projects = []
    for project in getProjectsForUser(user, False): # includePending=False
        projects.append( project.short_name )
    udict['projects'] = projects
    return udict
    

def share_projects(request):
    '''Shares the site's projects as a JSON-formatted list.'''
    
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
    
    
def share_user(request):
    '''Shares the user's access control memberships as a JSON-formatted document.'''
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # load User object by openid
        openid = request.GET['openid']
        userOpenid = get_object_or_404(UserOpenID, claimed_id=openid)
        
        users = { openid : serialize_user( userOpenid.user ) }
        
        response_data["users"] = users

        return HttpResponse(json.dumps(response_data, indent=4), content_type=JSON)

    else:
        return HttpResponseNotAllowed(['GET'])

    
    
def share_reload(request):
    '''Updates the list of remote projects in current database.'''
    
    if not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    sites = projectManager.reload()
    
    return HttpResponse(json.dumps(sites), content_type=JSON)
    
    