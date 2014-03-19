'''
Script to test insertion of a  user in the ESGF database.
'''

# first: must identify location of COG settings.py file
import os
import sys
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.contrib.auth.models import User
from cog.models import UserProfile

# insert given user
from cog.plugins.esgf.security import ESGFDatabaseManager
esgfDatabaseManager = ESGFDatabaseManager()

user = User(first_name='Test', last_name='User', username='testuser', email='testuser@test.com', password='abc123')
userProfile = UserProfile(user=user, institution='Institution', city='City', state='State', country='Country')

esgfUser = esgfDatabaseManager.insertUser(userProfile)

# verify user was inserted
esgfUser2 = esgfDatabaseManager.getUserByOpenid( esgfUser.openid )
print "Retrieved user with openid=%s" % esgfUser2.openid