'''
Script to test insertion of a  user in the ESGF database.
'''
import os
import sys
import cog

if __name__ == "__main__":

    # must identify location of COG settings.py file

    path = os.path.dirname(cog.__file__)
    sys.path.append( path )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    # insert given user
    from cog.plugins.esgf.security import ESGFDatabaseManager
    esgfDatabaseManager = ESGFDatabaseManager()
    esgfUser = esgfDatabaseManager.insertUser('Test', 'T', 'User', 'testuser@test.com', 'testuser', 'abc123', 'Organization', 'City', 'State', 'Country')

    # verify user was inserted
    esgfUser2 = esgfDatabaseManager.getUserByOpenid( esgfUser.openid )
    print "Retrieved user with openid=%s" % esgfUser2.openid