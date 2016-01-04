from django.shortcuts import render_to_response
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth.models import User
import datetime
from cog.models import UserProfile, Project
from cog.utils import getJson
from cog.models.peer_site import getPeerSites
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
import urllib
from collections import OrderedDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from cog.plugins.esgf.registry import LocalKnownProvidersDict

# module-scope object that holds list of known ESGF Identity Providers
# included here because login view is part of django-openid-auth module
esgf_known_providers = LocalKnownProvidersDict()

def paginate(objects, max_per_page, request):
    '''Utility method to paginate a list of objects before they are rendered in a template.'''
    
    page = getQueryDict(request).get('page')
    paginator = Paginator(objects, max_per_page) # show at most 'max_per_page'
    
    try:
        _objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _objects = paginator.page(paginator.num_pages)
    
    return _objects

def getKnownIdentityProviders():
    # sort dictionary by key
    return OrderedDict(sorted(esgf_known_providers.idpDict().items()))
    #return esgf_known_providers.idpDict()


# function to return an error message if a project is not active
def getProjectNotActiveRedirect(request, project):
        messages = ['Access to all pages of project %s is currently forbidden.' % project.short_name,
                    'Please contact <a href="/projects/cog/contactus/">support</a> with any questions.']
        return render_to_response('cog/common/message.html', 
                                  {'mytitle': 'Project Access Not Enabled',
                                   'project': project,
                                   'messages': messages},
                                  context_instance=RequestContext(request))


# function to return an error message if a project is not public
def getProjectNotVisibleRedirect(request, project):

        messages = ['Access to all pages of project %s is restricted to members only.' % project.short_name,
                    'Please contact <a href="/projects/cog/contactus/">support</a> with any questions.']
        return render_to_response('cog/common/message.html', 
                                  {'mytitle': 'Project Access Restricted',
                                   'project': project,
                                   'messages': messages},
                                  context_instance=RequestContext(request))


def set_openid_cookie(response, openid):
    """Utility method to consistently set the openid cookie."""
    
    print 'SETTING openid cookie to: %s' % openid
    
    response.set_cookie('openid', openid, 
                        expires=(datetime.datetime.now() + datetime.timedelta(days=3650)),  # expires in 10 years
                        httponly=True)


def getUsersThatMatch(match):
    """Returns the list of users that match a given expression."""
    
    return User.objects.filter((Q(username__icontains=match) | Q(first_name__icontains=match) |
                                Q(last_name__icontains=match) | Q(email__icontains=match)))


def get_projects_by_name(match):
    """Returns the list of users that match a given expression."""

    return Project.objects.filter((Q(short_name__icontains=match)))

def get_all_projects_for_user(user, includeCurrentSite=True):
    """Queries all nodes (including local node) for projects the user belongs to.
       Returns a list of dictionaries but does NOT update the local database.
       Example of JSON data retrieved from each node:
      {
        "users": {
            "https://hydra.fsl.noaa.gov/esgf-idp/openid/rootAdmin": {
                "home_site_domain": "cog-esgf.esrl.noaa.gov", 
                "openid": "https://hydra.fsl.noaa.gov/esgf-idp/openid/rootAdmin", 
                "datacart": {
                    "size": 0
                }, 
                "home_site_name": "NOAA ESRL ESGF-CoG", 
                "projects": {
                    "AlaskaSummerSchool": [
                        "admin", 
                        "user"
                    ], 
                    "CF-Grids": [
                        "admin"
                    ], 
                    "CFSS": [
                        "admin", 
                        "user"
                    ], 
                .....
    """

    # dictionary of information retrieved from each node, including current node
    projDict = {}  # node --> dictionary
    
    try:
        if user.profile.openid() is not None:
            
            openid = user.profile.openid()
            print 'Updating projects for user with openid=%s' % openid
            
            # loop over remote (enabled) nodes, possibly add current node
            sites = list(getPeerSites())
            if includeCurrentSite:
                sites = sites + [Site.objects.get_current()]
            for site in sites:
                            
                url = "http://%s/share/user/?openid=%s" % (site.domain, openid)
                print 'Updating user projects: querying URL=%s' % url
                jobj = getJson(url)
                if jobj is not None and openid in jobj['users']:
                    projDict[site] = jobj['users'][openid] 
                                                            
    except UserProfile.DoesNotExist:
        pass  # user profile not yet created
    
    # restructure information as list of (project object, user roles) tuples
    projects = []
    for psite, pdict in projDict.items():
        for pname, proles in pdict["projects"].items():
            try:
                proj = Project.objects.get(short_name__iexact=pname)
                projects.append((proj, proles))
            except ObjectDoesNotExist:
                pass

    # sort by project short name
    return projects

def add_get_parameter(url, key, value):
    """
    Utility method to add an HTTP request parameter to a GET request
    """
    
    if '?' in url:
        return url + "&%s" % urllib.urlencode([(key, value)])
    else:
        return url + "?%s" % urllib.urlencode([(key, value)])
    
def getQueryDict(request):
    '''Utiity method to return the query dictionary for a GET or POST request.'''
    
    if request.method == 'POST':
        return request.POST
    else:
        return request.GET
