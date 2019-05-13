'''
Views for exchanging information with other nodes.
'''
from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
import logging
import json
from cog.models import Project, getProjectsAndRolesForUsers, DataCart
from django.contrib.sites.models import Site
from cog.project_manager import projectManager
from cog.views.constants import PERMISSION_DENIED_MESSAGE
from django_openid_auth.models import UserOpenID
from django.contrib.auth.decorators import user_passes_test
from django.template import RequestContext
from django.conf import settings

from cog.services.registration import esgfRegistrationServiceImpl as registrationService
from cog.models.user_profile import UserProfile
from django.core.exceptions import ObjectDoesNotExist

log = logging.getLogger(__name__)

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
    
    # public or private
    pdict["private"] = str(project.private)
    
    # shared or local
    pdict["shared"] = str(project.shared)
    
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
              'home_site_name': user.profile.site.name,
              'home_site_domain': user.profile.site.domain,
              'project_tags': [x.name for x in user.profile.tags.all()] }
    
    # only include local projects
    udict['projects'] = getProjectsAndRolesForUsers(user, includeRemote=False)
    
    # data cart
    (dc, created) = DataCart.objects.get_or_create(user=user)
    udict['datacart'] = { 'size': len( dc.items.all() ) }
    
    # ESGF access control group - only if CoG installation is backed up by ESGF database
    if settings.ESGF_CONFIG:
        groups = registrationService.listByOpenid(user.profile.openid())
        udict['groups'] = groups
    else:
        udict['groups'] = {}
    
    return udict
    

def share_projects(request):
    '''Shares the node's projects as a JSON-formatted list.'''
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # current site
        current_site = Site.objects.get_current()
        response_data['site'] = serialize_site(current_site)
        
        # list projects from this node
        projects = {}
        log.debug('Listing ACTIVE projects for current site=%s' % current_site)
        for project in Project.objects.filter(active=True).filter(site=current_site):
            projects[project.short_name] = serialize_project(project)
            
        response_data["projects"] = projects   
        
        # list users from this node
        numberOfUsers = UserProfile.objects.filter(site=current_site).count()
        response_data["users"] = numberOfUsers   
        
        return HttpResponse(json.dumps(response_data, indent=4), content_type=JSON)
    else:
        return HttpResponseNotAllowed(['GET'])
    
def share_groups(request):
    '''Shares the node's access control groups as a JSON-formatted list.'''
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # current node
        current_site = Site.objects.get_current()
        response_data['site'] = serialize_site(current_site)
        
        # list groups from this node, index by group name
        log.debug('Listing visible groups for current site=%s' % current_site)
        groups = {}
        for group in registrationService.listGroups():
            if group['visible'] and group['name'].lower() != 'wheel':
                groups[ group['name'] ] = group          
        response_data["groups"] = groups
        
        return HttpResponse(json.dumps(response_data, indent=4), content_type=JSON)
    else:
        return HttpResponseNotAllowed(['GET'])
    
def share_user(request):
    '''Shares the user's access control memberships as a JSON-formatted document.'''
    
    if (request.method=='GET'):
        
        response_data = {}
        
        # load User object by openid
        openid = request.GET['openid']
        try:
            userOpenid = UserOpenID.objects.get(claimed_id=openid)
            users = { openid : serialize_user( userOpenid.user ) }
             
        except ObjectDoesNotExist:
            # return empty dictionary
            log.debug('User with openid=%s found at this site' % openid)
            users = {}
        
        response_data["users"] = users

        return HttpResponse(json.dumps(response_data, indent=4), content_type=JSON)

    else:
        return HttpResponseNotAllowed(['GET'])

    
    
@user_passes_test(lambda u: u.is_staff)
def sync_projects(request):
    '''Updates the list of remote projects in current database.'''
        
    sites, totalNumberOfProjects, totalNumberOfUsers = projectManager.sync()
    
    return render(request,
                  'cog/admin/sync_projects.html', 
                  {'sites':sorted(sites.iteritems(), key=lambda (siteid, sitedict): sitedict['name']), 
                   'totalNumberOfProjects':totalNumberOfProjects, 'totalNumberOfUsers':totalNumberOfUsers })
        
    