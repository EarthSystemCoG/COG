from cog.models import *
from cog.services.membership import *
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpRequest, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from cog.views.utils import getUsersThatMatch, getQueryDict
from django.contrib.sites.models import Site
from cog.models.auth import userHasAdminPermission
from cog.views.utils import paginate

from cog.notification import notify
from constants import PERMISSION_DENIED_MESSAGE

# HTTP parameters
NEW_MEMBERSHIP = "new_membership"
OLD_MEMBERSHIP = "old_membership"
NO_MEMBERSHIP = "no_membership"


# View to request a membership in a project, used for GET/POST requests
@login_required
def membership_request(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    title = '%s Project Membership Request' % project.short_name
    template = 'cog/membership/membership_request.html'

    # display submission form
    if request.method == 'GET':
        
        return render_to_response(template, {'project': project, 'title': title},
                                  context_instance=RequestContext(request))
        
    # process submission form
    else:
            
        # load user from authenticated request
        user = request.user
        
        # load or create group
        group = project.getUserGroup()

        # request membership
        status = requestMembership(user, group)
        
        # notify all project administrators
        if status == RESULT_SUCCESS:
            notifyAdminsOfMembershipRequest(project, user, request)
                
        return render_to_response(template, 
                                  {'project': project, 'group': group, 'user': user, 'status': status, 'title': title},
                                  context_instance=RequestContext(request))
    

# View to list the project memberships for all system users
@login_required
def membership_list_all(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # load all users - that match...
    match = getQueryDict(request).get('match', None) # works for GET or POST
    if match:
        users = getUsersThatMatch(match)
    else:
        users = User.objects.all().order_by('last_name')  
                  
    title = 'List All Users'
    view_name = 'membership_list_all'
    return render_membership_page(request, project, users, title, view_name)


# View to list the memberships for all users enrolled in the project
@login_required
def membership_list_enrolled(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # optional 'match' argument
    match = getQueryDict(request).get('match', None) # works for GET or POST
    
    if match:
        # filter all users by 'match'
        _users = getUsersThatMatch(match)
        # filter all users by project
        users = [user for user in _users if (user in project.getUserGroup().user_set.all() 
                                             or user in project.getAdminGroup().user_set.all())]     
    else:
        users = list(project.getUsers())
    
    title = '%s Current Users' % project.short_name
    view_name = 'membership_list_enrolled'
    return render_membership_page(request, project, users, title, view_name)


# View to list all the users waiting approval to join the project
@login_required
def membership_list_requested(request, project_short_name):
        
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # load user group
    group = project.getUserGroup()
    
    # optional 'match' argument
    match = getQueryDict(request).get('match', None) # works for GET or POST

    if match:
        # lookup specific user
        _users = [mr.user for mr in MembershipRequest.objects.filter(group=group).order_by('user__last_name')]
        users = [user for user in _users if (match in user.first_name.lower()
                                             or match in user.last_name.lower()
                                             or match in user.username.lower()
                                             or match in user.email.lower())]
    else:
        # load all users that have requested membership
        users = [mr.user for mr in MembershipRequest.objects.filter(group=group).order_by('user__last_name')]
             
    title = '%s Pending Users' % project.short_name   
    view_name = 'membership_list_requested'
    return render_membership_page(request, project, users, title, view_name)


def render_membership_page(request, project, users, title, view_name):
    
    # load project groups
    groups = project.getGroups()
        
    return render_to_response('cog/membership/membership_list.html', 
                              {'project': project, 
                               'users': paginate(users, request, max_counts_per_page=50),
                               'groups': groups,
                               'view_name': view_name,
                               'title': title, 'list_title': '%s Membership' % project.short_name},
                              context_instance=RequestContext(request))


# view to cancel membership in a project...initiated by the user from their profile page
# this view acts on the currently logged-in user
@login_required
def membership_remove(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # redirect to project home node?
    if project.site != Site.objects.get_current():
        url = 'http://%s%s' % (project.site.domain, reverse('membership_remove',
                                                            kwargs={'project_short_name': project.short_name}))
        return HttpResponseRedirect(url)
    
    template = 'cog/membership/membership_cancel.html'

    # display submission form
    if request.method == 'GET':
        
        title = 'Cancel %s Membership Request' % project.short_name
        return render_to_response(template, {'project': project, 'title': title},
                                  context_instance=RequestContext(request))
        
    # process submission form
    else:
        
        for group in [project.getAdminGroup(), project.getUserGroup(), project.getContributorGroup()]:
            # user is enrolled in group
            if group in request.user.groups.all():
                status = cancelMembership(request.user, group)
                if status == RESULT_SUCCESS:
                    notifyUserOfMembershipSelfCanceled(project, request.user)

            # user is pending approval in group
            else:
                cancelMembershipRequest(request.user, group)
                
        # just send one email for the project
        notifyAdminsOfMembershipCanceled(project, request.user)
        
        # redirect to confirmation page
        #title = 'Cancel %s Membership Confirmation' % project.short_name
        #return render_to_response(template, {'project':project,'title': title },
        # context_instance=RequestContext(request))
        # redirect to user profile (on proper node)
        return HttpResponseRedirect(reverse('user_profile_redirect', kwargs={'user_id': request.user.id}))
    

#view to bulk-process group membership operations from the pending_users or current_users template
#this view can be invoked as either GET or POST,  following a GET request to a membership listing
# @login_required
def membership_process(request, project_short_name):
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    queryDict = getQueryDict(request)
    
    for (name, value) in queryDict.items():

        if name.startswith(NEW_MEMBERSHIP) or name.startswith(OLD_MEMBERSHIP) or name.startswith(NO_MEMBERSHIP):
            (prefix, group_name, user_id) = name.split(":")
            
            group = get_object_or_404(Group, name=group_name)
            user = get_object_or_404(User, pk=user_id)
            
            # HTTP POST parameter from form check-box, all checks are treated as new
            # process checkbox as a new user
            if name.startswith(NEW_MEMBERSHIP):
                status = addMembership(user, group)

                #only email if user not already a member
                if status == RESULT_SUCCESS:
                    notifyUserOfMembershipGranted(project, group, user, request)

            # process hidden input field that indicates current membership
            # HTTP POST parameter from form hidden field
            # if user has a role, then {{isEnrolled}} turns on the hidden field with value = "on"

            elif name.startswith(OLD_MEMBERSHIP):
                try:
                    # don't delete from group if checkbox is still checked  (e.g. new membership)
                    new_membership = queryDict[encodeMembershipPar(NEW_MEMBERSHIP, group.name, user.id)]
                except KeyError:
                    # checkbox is empty, so remove from group
                    status = cancelMembership(user, group)
                    if status == RESULT_SUCCESS:
                        notifyUserOfGroupRemoval(project, group, user)
             
            # HTTP GET parameter (when delete link clicked)
            elif name.startswith(NO_MEMBERSHIP):
                # TODO check group here, should remove from all groups
                status = cancelMembership(user, group)
                if status == RESULT_SUCCESS:
                    notifyUserOfGroupRemoval(project, group, user)

    # redirect to the original listing that submitted the processing
    view_name = queryDict['view_name']
    return HttpResponseRedirect(reverse(view_name,
                                        kwargs={'project_short_name': project_short_name})+"?status=success")


# Utility method to encode a membership HTTP parameter as "action:group_name:user_id"
def encodeMembershipPar(action, group_name, user_id):
    return "%s:%s:%s" % (action, group_name, user_id)


def notifyAdminsOfMembershipRequest(project, user, request):
    url = reverse('membership_list_requested', kwargs={'project_short_name': project.short_name.lower()})
    url = request.build_absolute_uri(url)
    subject = "[%s] Membership Request" % project.short_name
    message = "User: %s has requested to join your ESGF-CoG Project: %s." \
              "\nYou may process this membership request at: %s." \
              % (user.username, project.short_name, url)
    for admin in list(project.getAdminGroup().user_set.all())+list(getSiteAdministrators()):
        notify(admin, subject, message)

def notifyUserOfMembershipGranted(project, group, user, request):
    
    subject = "[%s] Membership Granted" % project.short_name
    message = "Welcome %s! You have been granted membership in the ESGF-CoG Project: %s," \
              " and assigned to the %s permissions group." % (user.first_name, project.short_name, _getGroupDescription(group.name))
    
    url = project.home_page_url()
    url = request.build_absolute_uri(url)

    message += "\nPlease login and collaborate with us at: %s." % url
    notify(user, subject, message)


def notifyUserOfGroupRemoval(project, group, user):
    
    subject = "[%s] Permissions Group Modification" % project.short_name
    message = "Greetings %s. Your permissions in the ESGF-CoG Project: %s have changed." \
              "\nYou have been removed from the %s permissions group." % (user.first_name, project.short_name,
                                                                         _getGroupDescription(group.name) )
    notify(user, subject, message)
    

def notifyUserOfMembershipSelfCanceled(project, user):
    
    subject = "[%s] Membership Canceled" % project.short_name
    message = "As you requested, your membership in the ESGF-CoG Project: %s has been canceled." \
              "\nPlease contact the [%s] project administrators if you did not " \
              "request this action." % project.short_name
    notify(user, subject, message)
    
def _getGroupDescription(group_name):
    '''Returns a human readable description for a permissions group.'''
    
    parts = group_name.split('_')
    return parts[1].capitalize()


def notifyAdminsOfMembershipCanceled(project, user):

    subject = "[%s] Membership Canceled" % project.short_name
    message = "User %s has decided to cancel his/her membership in project %s." % (user.username, project.short_name)
    
    for admin in list(project.getAdminGroup().user_set.all())+list(getSiteAdministrators()):
        notify(admin, subject, message)