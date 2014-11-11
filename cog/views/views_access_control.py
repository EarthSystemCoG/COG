'''
Module containing views for managing access control groups.

@author: Luca Cinquini
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from sqlalchemy.orm.exc import NoResultFound

from cog.models import User, UserProfile, getSiteAdministrators
from cog.services.registration import esgfRegistrationServiceImpl as registrationService
from cog.plugins.esgf.objects import ROLE_USER, ROLE_PUBLISHER, ROLE_SUPERUSER, ROLE_ADMIN
from cog.forms import PermissionForm
from django.contrib.sites.models import Site
from cog.models import getPeerSites
from cog.utils import getJson
from django.core.urlresolvers import reverse
from collections import OrderedDict

from cog.notification import notify
from constants import PERMISSION_DENIED_MESSAGE, SAVED

@login_required
def ac_subscribe(request, group_name):
    '''
    View to request an access control permission.
    Currently, it can only be used to request ROLE_USER.
    '''
            
    title = '%s Data Access Request' % group_name
    template = 'cog/access_control/subscribe.html'

    # display submission form
    if request.method=='GET':
        
        status = registrationService.status(request.user.profile.openid(), group_name, ROLE_USER)
        
        return render_to_response(template, 
                                  {'title': title, 'group_name': group_name, 'status':status }, 
                                  context_instance=RequestContext(request))
        
    # process submission form
    else:
        
        approved = registrationService.subscribe(request.user.profile.openid(), group_name, ROLE_USER)
        
        # notify site administrators
        if not approved:
            notifyAdmins(group_name, request.user.id, request)
            
        # (GET-POST-REDIRECT)
        return HttpResponseRedirect( reverse('ac_subscribe', kwargs={'group_name': group_name }) + "?approved=%s" % approved)            
            
            
@login_required
def ac_process(request, group_name, user_id):
    '''
    View to process an access control permission request.
    This view can be used to assign any permissions to the user.
    '''
    
    # check site administrator privileges
    admin = request.user
    if not admin.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # load user
    user = get_object_or_404(User, pk=user_id)
    openid = user.profile.openid()

    title = '%s Data Access Management' % group_name
    template = 'cog/access_control/process.html'

    # display admin form
    if request.method=='GET':

        # set initial status of check boxes from database
        initial = {}
        permissions = registrationService.list(openid, group_name)
        for role, approved in permissions.items():
            initial['%sPermissionCheckbox' % role] = approved
        
        form = PermissionForm(initial=initial)
        
        return render_to_response(template, 
                                  {'group_name': group_name, 'title': title, 'user':user, 'form':form }, 
                                  context_instance=RequestContext(request))
    
    # process admin form
    else:
        form = PermissionForm(request.POST)

        if form.is_valid():

            # loop over roles
            for role in [ROLE_USER, ROLE_PUBLISHER, ROLE_SUPERUSER, ROLE_ADMIN]:
                # retrieve approve status from POST data and store it in ESGF database
                approve = form.cleaned_data.get('%sPermissionCheckbox' % role, False) # only True values are transmitted in POST data
                try:
                    registrationService.process(openid, group_name, role, approve)
                
                except NoResultFound: # permission not found in database    
                    if approve: # create new permission, but only if approve=True
                        registrationService.subscribe(openid, group_name, role)
                        registrationService.process(openid, group_name, role, approve)
                        
            # notify user
            permissions = registrationService.list(user.profile.openid(), group_name)
            notifyUser(group_name, request.user, permissions)
                

            # (GET-POST-REDIRECT)
            return HttpResponseRedirect( reverse('ac_process', kwargs={'user_id': user.id, 'group_name': group_name })
                                         + "?message=%s" % SAVED)            
            
        else:
            print "Form is invalid: %s" % form.errors
            return render_to_response(template, 
                                      {'group_name': group_name, 'title': title, 'user':user, 'form':form }, 
                                      context_instance=RequestContext(request))
            
def ac_list(request):
    '''
    View to display all access control groups that may be used to restrict data access.
    This view is intentionally open to the public (for now).
    '''
    
    # loop over local site + peer sites
    groups = {}
    sites = [Site.objects.get_current()] + getPeerSites()
    
    for site in sites:
        url = "http://%s/share/groups/" % site.domain
        jobj = getJson(url)
        if jobj is not None: # no error in fetching URL
            site_name = jobj['site']['name']
            site_domain =  jobj['site']['domain']

            # loop over groups for this site
            for group_name, group_dict in jobj['groups'].items():
                # augment group dictionary
                group_dict['site_name'] = site_name
                group_dict['site_domain'] = site_domain
                groups[group_name] = group_dict
                
    # order groups by name
    _groups = OrderedDict(sorted(groups.items()))
    
    return render_to_response('cog/access_control/list.html', 
                              {'groups': _groups, 'title': 'ESGF Data Access Control Groups' }, 
                              context_instance=RequestContext(request))
    
def notifyAdmins(group_name, user_id, incomingRequest):
    
    user = get_object_or_404(User, pk=user_id)

    subject = "'%s' Data Access Request" % group_name
    message = "User '%s' has requested membership in group '%s'" % (user.get_full_name(), group_name)
    message += '\nPlease process the request at: %s' % incomingRequest.build_absolute_uri( reverse('ac_process', kwargs={ 'group_name':group_name, 'user_id':user.id }) )

    # user attributes
    message +="\n"
    message += "\nFirst Name: %s" % user.first_name
    message += "\nLast Name: %s" % user.last_name
    message += "\nUser Name: %s" % user.username
    message += "\nEmail: %s" % user.email
    
    # openid
    message += "\nOpenID is: %s" % user.profile.localOpenid()

    # user profile attributes
    profile = UserProfile.objects.get(user=user)
    message += "\nInstitution: %s" % profile.institution
    message += "\nDepartment: %s" % profile.department
    message += "\nCity: %s" % profile.city
    message += "\nState: %s" % profile.state
    message += "\nCountry: %s" % profile.country

    for admin in getSiteAdministrators():
        notify(admin, subject, message)
        
def notifyUser(group_name, user, permissions):
    
    subject = "'%s' Data Access Notification" % group_name
    message = "Your permissions in group '%s' have been updated" % group_name
    
    for (role, status) in permissions.items():
        message += "\nRole: %s status=%s" % (role, status)
        
    notify(user, subject, message)
