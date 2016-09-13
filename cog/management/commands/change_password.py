'''
Django management command to update the list of CoG peer nodes in the local database.

Execute as:
python manage.py change_password user_openid new_password

Example: 
python manage.py change_password 'https://my.esgf.node/esgf-idp/openid/rootAdmin' my_secret

'''

from cog.plugins.esgf.security import esgfDatabaseManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django_openid_auth.models import UserOpenID


class Command(BaseCommand):
    
    args = '<openid new_password>'
    help = 'Changes the ESGF password of a user with a given openid'
    
    
    def handle(self, *args, **options):
        
        openid = args[0]
        new_password = args[1]
        
        self.stdout.write("Setting new password=%s for openid=%s" % (new_password, openid) )
        
        
        try:
            # retrieve user from CoG database
            userOpenid = UserOpenID.objects.get(claimed_id=openid)
            
            # update password in ESGF database
            esgfDatabaseManager.updatePassword(userOpenid.user, new_password)
            
        except ObjectDoesNotExist:
            self.stdout.write("User with openid=%s not found in local database." % openid)
        