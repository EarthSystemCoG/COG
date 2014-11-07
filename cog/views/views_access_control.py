'''
Module containing views for managing access control groups.

@author: Luca Cinquini
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from sqlalchemy.orm.exc import NoResultFound

from cog.models import User
from cog.services.registration import esgfRegistrationServiceImpl as registrationService
from cog.plugins.esgf.objects import ROLE_USER, ROLE_PUBLISHER, ROLE_SUPERUSER, ROLE_ADMIN
from cog.forms import PermissionForm

from cog.notification import notify
from constants import PERMISSION_DENIED_MESSAGE, SAVED

@login_required
def ac_subscribe(request, user_id, group_name):
    '''
    View to request an access control permission.
    Currently, it can only be used to request ROLE_USER.
    '''
    
    # load user
    user = get_object_or_404(User, pk=user_id)
    if user.id != request.user.id:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
    title = '%s Data Access Request' % group_name
    template = 'cog/access_control/subscribe.html'

    # display submission form
    if request.method=='GET':
        
        return render_to_response(template, 
                                  {'group_name': group_name, 'title': title}, 
                                  context_instance=RequestContext(request))
        
    # process submission form
    else:
        
        approved = registrationService.subscribe(user.profile.openid(), group_name, ROLE_USER)
        
        # notify site administrators
        # TODO
        
        # return feedback to user
        return render_to_response(template, 
                                  {'group_name': group_name, 'title': title, 'approved':approved }, 
                                  context_instance=RequestContext(request))

            
            
@login_required
def ac_process(request, user_id, group_name):
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
                print 'processing role=%s approve=%s' % (role, approve)
                try:
                    registrationService.process(openid, group_name, role, approve)
                
                except NoResultFound: # permission not found in database    
                    if approve: # create new permission, but only if approve=True
                        registrationService.subscribe(openid, group_name, role)
                        registrationService.process(openid, group_name, role, approve)

            # (GET-POST-REDIRECT)
            return HttpResponseRedirect( reverse('ac_process', kwargs={'user_id': user.id, 'group_name': group_name })
                                         + "?message=%s" % SAVED)            
            
        else:
            print "Form is invalid: %s" % form.errors
            return render_to_response(template, 
                                      {'group_name': group_name, 'title': title, 'user':user, 'form':form }, 
                                      context_instance=RequestContext(request))