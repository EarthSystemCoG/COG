'''
Implementation of RegistrationService backed-up by the ESGF access control object model
(NOT by django-managed objects).

@author: Luca Cinquini
'''

from cog.services.registration import RegistrationService
from cog.plugins.esgf.security import esgfDatabaseManager

class ESGFRegistrationServiceImpl(RegistrationService):
    '''Implementation of RegistrationService that is a thin wrapper around the ESGFDatabaseManager.'''
    
    def __init__(self, esgfDatabaseManager):
        self.esgfDatabaseManager = esgfDatabaseManager
        
    def subscribe(self, userOpenid, groupName, roleName):
        
        # check for existing permission
        approved = self.esgfDatabaseManager.permissionDao.readPermission(userOpenid, groupName, roleName) 
        
        # if not found crate a new one
        if approved is None:
            approved = self.esgfDatabaseManager.permissionDao.createPermission(userOpenid, groupName, roleName)
            
        return approved
        
    def process(self, userOpenid, groupName, roleName, approve):
        
        self.esgfDatabaseManager.permissionDao.updatePermission(userOpenid, groupName, roleName, approve) 
        
    def status(self, userOpenid, groupName, roleName):
        
        # check for existing permission
        # will return None if the permission is not found
        return self.esgfDatabaseManager.permissionDao.readPermission(userOpenid, groupName, roleName) 
            
        
    def list(self, userOpenid, groupName):
        
        return self.esgfDatabaseManager.permissionDao.readPermissions(userOpenid, groupName) 

    
    def createGroup(self, name, description='', visible=True, automatic_approval=False):
        
        return self.esgfDatabaseManager.createGroup(name, description=description, visible=visible, automatic_approval=automatic_approval)
    
esgfRegistrationServiceImpl = ESGFRegistrationServiceImpl(esgfDatabaseManager)