from cog.models import *
from cog.services.membership import *
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpRequest, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required

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
    
    title = '%s Group Membership Request' % project.short_name
    template = 'cog/membership/membership_request.html'

    # display submission form
    if request.method=='GET':
        
        return render_to_response(template, {'project':project,'title': title }, context_instance=RequestContext(request))
        
    # process submission form
    else:
            
        # load user from authenticated request
        user = request.user
        
        # load or create group
        group = project.getUserGroup()

        # request membership
        status = requestMembership(user, group)
        
        # notify all project administrators
        if status==RESULT_SUCCESS:
            notifyAdminsOfMembershipRequest(project, group, user, request)
                
        return render_to_response(template, 
                                  {'project':project, 'group':group, 'user':user, 'status':status, 'title': title }, 
                                  context_instance=RequestContext(request))
    
# View to list the project memberships for all system users
@login_required
def membership_list_all(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # load all users
    if request.method=='GET':
    
        users = User.objects.all().order_by('last_name')
        title = 'List All System Users'
    
    # lookup specific user
    else:
        
        match = request.POST['match']
        users = User.objects.filter( ( Q(username__icontains=match) | Q(first_name__icontains=match) | Q(last_name__icontains=match) | Q(email__icontains=match) ) )
        title = 'Lookup System User'
        
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
    
    # load all project users
    # (must return a list for pagination)
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
    
    # load users that have requested membership
    # order by username
    users = [mr.user for mr in MembershipRequest.objects.filter(group=group).order_by('user__last_name')]
    
    title = '%s Pending Users' % project.short_name   
    view_name = 'membership_list_requested'
    return render_membership_page(request, project, users, title, view_name)

def render_membership_page(request, project, users, title, view_name):
    
    # load project groups
    groups = project.getGroups()
        
    return render_to_response('cog/membership/membership_list.html', 
                              {'project':project, 'users':users, 'groups':groups, 
                               'view_name':view_name,
                               'title': title, 'list_title':'%s Membership' % project.short_name }, 
                              context_instance=RequestContext(request))

# view to cancel user's own membership in a project
# this view acts on the currently logged-in user
@login_required
def membership_remove(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    template = 'cog/membership/membership_cancel.html'
    # display submission form
    if request.method=='GET':
        
        title = 'Cancel %s Membership Request' % project.short_name
        return render_to_response(template, {'project':project,'title': title}, context_instance=RequestContext(request))
        
    # process submission form
    else:
            
        for group in [project.getAdminGroup(), project.getUserGroup()]:
            # user is enrolled in group
            if group in request.user.groups.all():
                status = cancelMembership(request.user, group)
                if status==RESULT_SUCCESS:
                    notifyUserOfMembershipSelfCanceled(project, group, request.user)
            # user is pending approval in group
            else:
                cancelMembershipRequest(request.user, group)
                
        # just send one email for the project
        notifyAdminsOfMembershipCanceled(project, request.user)
        
        title = 'Cancel %s Membership Confirmation' % project.short_name
        return render_to_response(template, {'project':project,'title': title }, context_instance=RequestContext(request))   
    
# view to bulk-process group membership operations
# this view can be invoked as either GET or POST,  following a GET request to a membership listing
@login_required
def membership_process(request, project_short_name):
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    for (name, value) in request.REQUEST.items():
                
        if name.startswith(NEW_MEMBERSHIP) or name.startswith(OLD_MEMBERSHIP) or name.startswith(NO_MEMBERSHIP):
            (prefix, group_name, user_id) = name.split(":")
            
            group = get_object_or_404(Group, name=group_name)
            user = get_object_or_404(User, pk=user_id)
            
            # HTTP POST parameter from form check-box
            if name.startswith(NEW_MEMBERSHIP):
                status = addMembership(user, group)
                if status==RESULT_SUCCESS:
                    notifyUserOfMembershipGranted(project, group, user, request)
                
            # HTTP POST parameter from form hidden field
            elif name.startswith(OLD_MEMBERSHIP):
                try:
                    # do not remove is new_membership parameter is found
                    new_membership = request.REQUEST[encodeMembershipPar(NEW_MEMBERSHIP, group.name,user.id)]
                except KeyError:
                    status = cancelMembership(user, group)
                    if status==RESULT_SUCCESS:
                        notifyUserOfMembershipCanceled(project, group, user)
             
            # HTTP GET parameter       
            elif name.startswith(NO_MEMBERSHIP):
                status = cancelMembership(user, group)
                if status==RESULT_SUCCESS:
                    notifyUserOfMembershipCanceled(project, group, user)
        
    # redirect to the original listing that submitted the processing   
    view_name = request.REQUEST['view_name']
    return HttpResponseRedirect( reverse(view_name, kwargs={'project_short_name': project_short_name })+"?status=success" )

# Utility method to encode a membership HTTP parameter as "action:group_name:user_id"
def encodeMembershipPar(action, group_name, user_id):
    return "%s:%s:%s" % (action, group_name, user_id)

def notifyAdminsOfMembershipRequest(project, group, user, request):
    url = reverse('membership_list_requested', kwargs={ 'project_short_name':project.short_name.lower() })
    url = request.build_absolute_uri(url)
    subject = "[%s] Membership Request" % project.short_name
    message = "User: %s has requested to join project: %s.\nPlease process the membership request at: %s ." \
            % (user.username, project.short_name, url)
    for admin in list(project.getAdminGroup().user_set.all())+list(getSiteAdministrators()):
        notify(admin, subject, message)


def notifyUserOfMembershipGranted(project, group, user, request):
    
    subject = "[%s] Membership Granted" % project.short_name
    message = "You have been granted membership in group: %s.\nThank you for your interest in project: %s." % (group.name, project.short_name)
    
    url = project.home_page_url()
    url = request.build_absolute_uri(url)
    message += "\nPlease visit the %s project workspace at: %s" % (project.short_name, url)
    notify(user, subject, message)

def notifyUserOfMembershipCanceled(project, group, user):
    
    subject = "[%s] Membership Canceled" % project.short_name
    message = "We are sorry to inform you that your membership in group: %s has been canceled.\nPlease contact the administrators of project: %s for any questions." % (group.name, project.short_name)
    notify(user, subject, message)
    
def notifyUserOfMembershipSelfCanceled(project, group, user):
    
    subject = "[%s] Membership Canceled" % project.short_name
    message = "As you requested, your membership in group: %s has been canceled.\nPlease contact the administrators of project: %s immediately if you did not request this cancellation." % (group.name, project.short_name)
    notify(user, subject, message)
    
def notifyAdminsOfMembershipCanceled(project, user):
    
    subject = "[%s] Membership Canceled" % project.short_name
    message = "User %s has decided to cancel his/her membership in project %s." % (user.username, project.short_name)
    
    for admin in list(project.getAdminGroup().user_set.all())+list(getSiteAdministrators()):
        notify(admin, subject, message)