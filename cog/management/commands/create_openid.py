'''
Django management command to create a local OpenID for a given user.
The supplied password will be set both on the CoG portal and ESGF node.
Execute as:
python manage.py create_openid <username> <password>
'''

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from cog.plugins.esgf.security import esgfDatabaseManager
import datetime

class Command(BaseCommand):
    
    help = 'Create OpenID for given username (with password).'
       
    def handle(self, *ags, **options):
        
        if settings.ESGF_CONFIG and settings.ESGF_HOSTNAME:
            
            username = ags[0]
            password = ags[1]
            user = User.objects.get(username=username)
            openid = user.profile.localOpenid() 
            
            if openid is None:
                user.set_password(password)
                user.save()
                user.profile.last_password_update = datetime.datetime.now()
                user.profile.save()
                user.profile.clearTextPassword = password
                esgfDatabaseManager.insertUser(user.profile)
                
            else:
                print 'User: %s already has a local openid: %s' % (user, openid)
        
        else:
            print 'ERROR: ESGF_HOSTNAME must be defined in file cog_settings.cfg'