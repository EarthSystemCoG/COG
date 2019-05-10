"""
Service module to manage membership of users in groups.
All methods return a string code that summarizes the result of the invocation.
Currently the underlying membership model includes only users and groups, no roles.
Note that the service methods do NOT include the notification functionality, which is left in the view layer.
This is because notification messages may include link to web pages (which are built from the request object),
and reference projects, as opposed to groups.
"""
from django.contrib.auth.models import User, Group, Permission
from cog.models import (MembershipRequest, ManagementBodyMember, OrganizationalRoleMember, 
                        getProjectForGroup, CommunicationMeansMember, LoggedEvent)
from django.core.urlresolvers import reverse
import django.dispatch

import logging

log = logging.getLogger(__name__)

# return codes
RESULT_SUCCESS = 'SUCCESS'
RESULT_DUPLICATE = 'DUPLICATE'
RESULT_NOT_FOUND = 'NOT FOUND'

# Method to request membership of a user in a group (with no role specification)
# Returns the status of the request: REQUESTED, DUPLICATE, REJECTED etc.
def requestMembership(user, group):
    
    try:
        gr = MembershipRequest.objects.get(user=user, group=group)
        return RESULT_DUPLICATE
    except MembershipRequest.DoesNotExist:
        gr = MembershipRequest(user=user, group=group)
        gr.save()
        return RESULT_SUCCESS
    
# Method to cancel a single membership request
def cancelMembershipRequest(user, group):
    # remove the entry from the unprocessed membership list
    mrlist = MembershipRequest.objects.filter(group=group).filter(user=user)
    if len(mrlist)>0:
        for mr in mrlist:
            log.debug('Cancelling membership request for user=%s group=%s' % (user.username, group.name))
            mr.delete()
            
# Method to cancel ALL membership requests for a given user, project
def cancelMembershipRequests(user, project):
    
    for group in [project.getAdminGroup(), project.getUserGroup(), project.getContributorGroup()]:
        cancelMembershipRequest(user, group)
        
# Method to enroll a user in a group (with no role specification)
def addMembership(user, group, admin=None):
    
    project = getProjectForGroup(group)
    
    if not group in user.groups.all():
        user.groups.add(group)
        log.debug("Enrolled user=%s in group=%s" % (user.username, group.name))
        cancelMembershipRequests(user, project)
        # log event
        if admin is not None:
            event = LoggedEvent.objects.create(user=admin, project=project, 
                                               title="Membership added", 
                                               description="Administrator: %s added user: %s to group: %s" % (admin, user, group.name))
            event.save()
        return RESULT_SUCCESS
    
    else:
        log.debug("User=%s is already enrolled in group=%s" % (user.username, group.name))
        cancelMembershipRequests(user, project)
        return RESULT_DUPLICATE

# Method to disenroll a user from a group
# Will also remove the user from any governance role for that project
def cancelMembership(user, group, admin=None):
     
    # cancel all requests for that project
    project = getProjectForGroup(group)
    cancelMembershipRequests(user, project)
    
    if group in user.groups.all():
           
        # first remove user from that group
        user.groups.remove(group)
        log.debug("Removed user=%s from group=%s" % (user.username, group.name))
        
        # if user is not part of the project any more, remove from all project management bodies
        project = getProjectForGroup(group)
        if not project.hasUser(user):
            # Management Bodies
            objs = ManagementBodyMember.objects.filter(user=user).filter(managementBody__project=project)
            for obj in objs:
                log.debug('Deleting ManagementBodyMember for project=%s user=%s managementBody=%s' % (project, user, obj.managementBody.title))
                obj.delete()
            # Organization Roles
            objs = OrganizationalRoleMember.objects.filter(user=user).filter(organizationalRole__project=project)
            for obj in objs:
                log.debug('Deleting OrganizationalRoleMember for project=%s user=%s organizationalRole=%s' % (project, user, obj.organizationalRole.title))
                obj.delete()
            # Communication Means
            objs = CommunicationMeansMember.objects.filter(user=user).filter(communicationMeans__project=project)
            for obj in objs:
                log.debug('Deleting CommunicationMeansMember for project=%s user=%s communicationMeans=%s' % (project, user, obj.communicationMeans.title))
                obj.delete()
            
        # log event
        if admin is not None:
            event = LoggedEvent.objects.create(user=admin, project=project, 
                                               title="Membership canceled", 
                                               description="Administrator: %s removed user: %s from group: %s" % (admin, user, group.name))
            event.save()

            
        return RESULT_SUCCESS
    
    else:
        log.debug("User=%s not found in group=%s" % (user.username, group.name))
        return RESULT_NOT_FOUND