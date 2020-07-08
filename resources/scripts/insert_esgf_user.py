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

# cleanup from previous executions
for user in User.objects.filter(username='testuser'):
    user.delete()

# insert given user
from cog.plugins.esgf.security import ESGFDatabaseManager
esgfDatabaseManager = ESGFDatabaseManager()

user = User.objects.create(first_name='Test', last_name='User', username='testuser', email='testuser@test.com', password='abc123')
userProfile = UserProfile.objects.create(user=user, institution='Institution', city='City', state='State', country='Country')

#esgfUser = esgfDatabaseManager.insertUser(userProfile)
openid = ''
for userOpenID in user.useropenid_set.all():
    openid = userOpenID.claimed_id
    print('User openid=%s' % openid)

# verify user was inserted
esgfUser2 = esgfDatabaseManager.getUserByOpenid( openid )
print("Retrieved user with openid=%s" % esgfUser2.openid)

# cleanup tgis execution
user.delete()