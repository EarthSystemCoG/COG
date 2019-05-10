'''
Script to migrate users to the ESGF database. Rules:
1) non-local users (i.e. users that logged onto CoG with an external openid) are ignored

2) if a user is local but has no local openid, look for ESGF users with that same email:
    a) if found, try to associate that openid to the CoG user, if possible
    b) if for any reason the openid cannot be associated, generate a new local openid and push it to the ESGF database

3) if a user is local and already has a local openid:
    - if that openid does not exist in ESGF database, push it
    
NOTE: passwords cannot be migrated from CoG to ESGF, they will need to be reset by the users.

@author: cinquini
'''

import os
import sys
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from django_openid_auth.models import UserOpenID

from cog.models import UserProfile
from cog.plugins.esgf.security import ESGFDatabaseManager

esgfDatabaseManager = ESGFDatabaseManager()

if settings.ESGF_CONFIG:
    
    # loop over CoG users
    for user in User.objects.all():
        
        # make sure user profile exists
        try:
            userp = user.profile
        except ObjectDoesNotExist:
            userp = UserProfile.objects.create(user=user)
            
        # select local users:
        if userp.type==1:
            
            # 1) CoG users with no local openid
            if len(userp.localOpenids())==0:
                
                # look for user email in ESGF database
                esgfUsers = esgfDatabaseManager.getUsersByEmail(user.email)
                
                # migrate CoG user --> ESGF user
                if len(esgfUsers)==0:                
                    esgfDatabaseManager.insertUser(userp)
                    
                # associate local ESGF openid(s) to CoG user; if none is found, create a new local openid
                else:
                    found = False
                    for esgfUser in esgfUsers:
                        # only assign if openid is local, and contains the CoG username
                        if settings.ESGF_HOSTNAME in esgfUser.openid and user.username in esgfUser.openid:
                            if not UserOpenID.objects.filter(claimed_id=esgfUser.openid).exists():
                                openid = UserOpenID.objects.create(user=user, claimed_id=esgfUser.openid, display_id=esgfUser.openid)
                                print('Assigned ESGF openid=%s to CoG user=%s' % (openid.claimed_id, user))
                                found = True
                    if not found:
                        esgfDatabaseManager.insertUser(userp)
                        
            # 2) CoG user with local openid(s)
            else:
                for openid in userp.localOpenids():
                    # make sure openid exists in ESGF database, if not migrate user
                    if esgfDatabaseManager.getUserByOpenid(openid) is None:
                        esgfDatabaseManager.insertUser(userp)
                        
                            
        else:
            #print "Ignoring non-local user: %s" % user
            pass