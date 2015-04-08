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

from cog.plugins.esgf.idp_whitelist import LocalKnownProvidersDict

# module-scope object that holds list of known ESGF Identity Providers
# included here because login view is part of django-openid-auth module
esgf_known_providers = LocalKnownProvidersDict()


def getKnownIdentityProviders():
    return esgf_known_providers.idpDict()


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


def get_all_projects_for_user(user, includeCurrentSite=True):
    """Queries all nodes (including local node) for projects the user belongs to.
       Returns a list of dictionaries but does NOT update the local database.
       Example of JSON data retrieved from each site:
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

    # dictionary of information retrieved from each site, including current site
    projDict = {}  # site --> dictionary
    
    try:
        if user.profile.openid() is not None:
            
            openid = user.profile.openid()
            print 'Updating projects for user with openid=%s' % openid
            
            # loop over remote (enabled) sites, possibly add current site
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