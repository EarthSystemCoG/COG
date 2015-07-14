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
    
    # FIXME
    if user.last_name=='Cinquini':
    
        for ugroup in user.groups.all():
            
            print 'user=%s group=%s' % (user, ugroup)
            if '_users' in ugroup.name:
                try:
                    project = getProjectForGroup(ugroup)
                    # remove 'user' group
                    user.groups.remove( ugroup )
                    # add 'contributor' group
                    cgroup = project.getContributorGroup()
                    print '\tUser %s: changing group %s to %s' % (user, ugroup, cgroup)
                    user.groups.add( cgroup )
                    user.save()
                except Project.DoesNotExist:
                    pass # old project ?
                        
    for permission in user.user_permissions.all():
        print '\tuser=%s permission=%s' % (user, permission)