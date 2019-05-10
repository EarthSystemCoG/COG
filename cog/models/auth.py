# module containing roles and permissions for access control
# functionality is based on django.contrib.auth

from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from constants import APPLICATION_LABEL, ROLE_ADMIN, ROLE_CONTRIBUTOR, ROLE_USER

import logging

log = logging.getLogger(__name__)

# GROUPS
def createGroup(group_name):
    group = Group(name=group_name)
    group.save()
    log.debug("Created group: %s" % group.name)
    return group

# method to load a named group from the database, or create a new one if not existing already
def getOrCreateGroup(group_name):
    try:       
        return Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return createGroup(group_name)
    
# method to build the group name of projects users
def getUserGroupName(project):
    return "%s_users" % project.short_name.lower()

# method to build the group name of projects contributors
def getContributorGroupName(project):
    return "%s_contributors" % project.short_name.lower()

# method to build the group name of project administrators
def getAdminGroupName(project):
    return "%s_admins" % project.short_name.lower()

# PERMISSIONS

# method to create a project permission
# and assign it to the given groups
def createProjectPermission(pDesc, pCodeName, groups):
        projectContenType = ContentType.objects.get(app_label=APPLICATION_LABEL, model='project')
        permission = Permission(name=pDesc, codename=pCodeName, content_type=projectContenType)
        permission.save()
        log.debug('Created permission=%s...' % permission.codename)
        for group in groups:
            group.permissions.add(permission)
            group.save()
            log.debug('...and associated to group=%s' % group.name)
        return permission

# method to return a named permission from the database, 
# or create a new one for these groups if not existing already
def getOrCreateProjectPermission(pDesc, pCodeName, groups):
    try:       
        return Permission.objects.get(codename=pCodeName)
    except Permission.DoesNotExist:
        return createProjectPermission(pDesc, pCodeName, groups)               

# shortcut method to check whether a user has 'user' permission for a given project
# note: now this method works directly on groups: a local staff user may NOT be in the user group for a remote project
def userHasUserPermission(user, project):
   
    if userHasContributorPermission(user, project): # NOTE: the 'contributor' role automatically guarantees 'user' privileges
        return True
    else:
        return project.getUserGroup() in user.groups.all()

# shortcut method to check whether a user has 'contributor' permission for a given project
def userHasContributorPermission(user, project):
    
    if userHasAdminPermission(user, project): # NOTE: the 'admin' role automatically guarantees 'contributor' privileges
        return True
    else:
        return project.getContributorGroup() in user.groups.all()

# shortcut method to check whether a user has 'admin' permission for a given project
# note: a local staff user may NOT be in the admin group for a remote project
def userHasAdminPermission(user, project):
    
    return (user.is_staff and project.isLocal()) or project.getAdminGroup() in user.groups.all()

# method to return the full permission label: cog.<pCodeName>
# used to check for user.has_perm(getPermissionLabel(project.getUserPermission()))
#def getPermissionLabel(permission):
#    return "%s.%s" % (APPLICATION_LABEL, permission.codename)


# ROLES

def userHasProjectRole(user, project, role):
    
    if role == ROLE_USER:
        return userHasUserPermission(user, project)
    elif role == ROLE_CONTRIBUTOR:
        return userHasContributorPermission(user, project)
    elif role == ROLE_ADMIN:
        return userHasAdminPermission(user, project)
    else:
        return False


