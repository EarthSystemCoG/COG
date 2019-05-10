'''
Script to migrate all current users from role=user to role=contributor
'''
import os, sys, cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django import setup as django_setup
django_setup()

from django.contrib.auth.models import User, Permission, Group
from cog.models import Project, getProjectForGroup

# loop over users
for user in User.objects.all():
    
    print('Processing user=%s' % user)
    
    # FIXME
    #if user.last_name=='Cinquini':
    
    for ugroup in user.groups.all():        

        if '_users' in ugroup.name:
            try:
                project = getProjectForGroup(ugroup)
                # remove 'user' group
                user.groups.remove( ugroup )
                # add 'contributor' group
                cgroup = project.getContributorGroup()
                print('\tUser %s: changing group %s to %s' % (user, ugroup, cgroup))
                user.groups.add( cgroup )
                user.save()
            except Project.DoesNotExist:
                pass # old project ?
                        
    # delete obsolete Permission objects
    for permission in user.user_permissions.all():
        if 'Admin Permission' in permission.name or 'User Permission' in permission.name:
            print('\tUser: %s deleting permission: %s' % (user, permission))
            user.user_permissions.remove(permission)
            user.save()
            permission.delete()