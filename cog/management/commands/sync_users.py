'''
Django management command to delete stale stubs for non-local user accounts that have been deleted at their home nodes.
Execute as:
python manage.py sync_users
'''

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cog.models.user_profile import isUserLocal
import urllib

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_NOT_FOUND = 404

class Command(BaseCommand):
    
    help = 'Deletes stale stub accounts that have been removed at their remote home CoG'
       
    def handle(self, *ags, **options):
        
        # loop over non-local users
        for user in User.objects.all():
            if not isUserLocal(user):
                
                # test user existence by accessing the profile page
                userProfileUrl = user.profile.getAbsoluteUrl()
                print "\nChecking user: %s url: %s" % (user, userProfileUrl)
                
                try:
                    response = urllib.urlopen( userProfileUrl )
                    if response.getcode()==HTTP_STATUS_CODE_NOT_FOUND:
                        
                        print '\tUser not found on remote node %s, deleting from local database...' % user.profile.site.domain
                        # delete this user from local database
                        user.delete()
                    else:
                        print '\tUser found.'
                         
                # remote node is not up   
                except IOError: # [Errno socket error] [Errno 61] Connection refused
                    print 'URL %s cannot be reached, skipping... ' % userProfileUrl