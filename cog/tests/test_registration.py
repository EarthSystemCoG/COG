'''
Created on Nov 4, 2014

@author: cinquini
'''

import os
import sys
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import unittest
from cog.plugins.esgf.security import esgfDatabaseManager
from cog.services.registration import ESGFRegistrationServiceImpl
from cog.plugins.esgf.objects import ROLE_USER, ROLE_PUBLISHER, ROLE_SUPERUSER, ROLE_ADMIN

TEST_OPENID = 'https://hydra.fsl.noaa.gov/esgf-idp/openid/lucacinquini' # FIXME: must exist
TEST_GROUP_A = 'NOAA ESRL' # Automatic approval group FIXME: must exist
TEST_GROUP_B = 'NCPP DIP'  # Non-automatic approval group FIXME: must exist

#TEST_GROUP = 'MyTestGroup'
#TEST_OPENID = "MyTestOpenid"


class Test(unittest.TestCase):


    def setUp(self):
        
        self.registrationService = ESGFRegistrationServiceImpl(esgfDatabaseManager)


    def tearDown(self):
        pass

    def testUserRegistration(self):

        # new permission
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_A, ROLE_USER)
        self.assertTrue(approved)
        
        # existing permission - same result
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_A, ROLE_USER)
        self.assertTrue(approved)
        
        # more restricted roles always require approval
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_A, ROLE_ADMIN)
        self.assertFalse(approved)
        
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_A, ROLE_PUBLISHER)
        self.assertFalse(approved)
        
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_A, ROLE_SUPERUSER)
        self.assertFalse(approved)
        
        # approve user
        self.registrationService.process(TEST_OPENID, TEST_GROUP_A, ROLE_SUPERUSER, True)
        approved = self.registrationService.status(TEST_OPENID, TEST_GROUP_A, ROLE_SUPERUSER)
        self.assertTrue(approved)
        
        # reject user
        self.registrationService.process(TEST_OPENID, TEST_GROUP_A, ROLE_SUPERUSER, False)
        approved = self.registrationService.status(TEST_OPENID, TEST_GROUP_A, ROLE_SUPERUSER)
        self.assertFalse(approved)

        # group with non-automatic approval
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_B, ROLE_USER)
        self.assertFalse(approved)
        
        # existing permission - same result
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_B, ROLE_USER)
        self.assertFalse(approved)
        
        # more restricted roles always require approval
        approved = self.registrationService.subscribe(TEST_OPENID, TEST_GROUP_B, ROLE_ADMIN)
        self.assertFalse(approved)
        
        # list permissions for automatic approval group
        permissions = self.registrationService.list(TEST_OPENID, TEST_GROUP_A)
        self.assertTrue(permissions[ROLE_USER])
        self.assertFalse(permissions[ROLE_ADMIN])
        self.assertFalse(permissions[ROLE_PUBLISHER])
        self.assertFalse(permissions[ROLE_SUPERUSER])
        
        # list permissions for manual approval group
        permissions = self.registrationService.list(TEST_OPENID, TEST_GROUP_B)
        self.assertFalse(permissions[ROLE_USER])
        self.assertFalse(permissions[ROLE_ADMIN])
        self.assertRaises(KeyError, permissions.get(ROLE_PUBLISHER))
        self.assertRaises(KeyError, permissions.get(ROLE_SUPERUSER))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()