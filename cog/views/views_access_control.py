'''
Module containing views for managing access control groups.

@author: Luca Cinquini
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from cog.models import User
from cog.services.registration import esgfRegistrationServiceImpl as registrationService
from cog.plugins.esgf.objects import ROLE_USER, ROLE_PUBLISHER, ROLE_SUPERUSER, ROLE_ADMIN

from cog.notification import notify
from constants import PERMISSION_DENIED_MESSAGE

@login_required
def subscribe(request, user_id, group_name):
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

            
            