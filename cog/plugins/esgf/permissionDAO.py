'''
Class to manage Permission objects in the ESGF database.

@author: Luca Cinquini
'''

from sqlalchemy.orm.exc import NoResultFound
from cog.plugins.esgf.objects import ESGFGroup, ESGFRole, ESGFUser, ESGFPermission, ROLE_USER

class PermissionDAO(object):
    
    def __init__(self, Session):
        
        # session factory
        self.Session = Session
        
    def createPermission(self, userOpenid, groupName, roleName):
        '''
        Method to create a new ESGF permission in the database.
        The approved status will depend on the group automatic_approval flag if the requested role is "user", 
        otherwise it will always have to be approved by the group administrator.
        Will throw an exception if the permission already exists.
        '''
        try:
            session = self.Session()
            
            (esgfUser, esgfGroup, esgfRole) = self._getPermissionObjects(session, userOpenid=userOpenid, groupName=groupName, roleName=roleName)
                               
            # create and store a new  permission
            # will throw IntegrityError if the permission already exists
            if roleName == ROLE_USER and esgfGroup.automatic_approval:
                approved = True
            else:
                approved = False
            p = ESGFPermission(user=esgfUser, group=esgfGroup, role=esgfRole, approved=approved)
            
            session.add(p)
            session.commit()
            
            # return approved status
            return p.approved
                            
        finally:
            session.close()
            
    def readPermission(self, userOpenid, groupName, roleName):
        '''
        Method to read the approved status of an existing ESGF permission in the database.
        Will return None if the permission does not exist.
        '''
        
        try:
            session = self.Session()
            
            (esgfUser, esgfGroup, esgfRole) = self._getPermissionObjects(session, userOpenid=userOpenid, groupName=groupName, roleName=roleName)
                                           
            try:
                # retrieve an existing permission
                # will throw NoResultFound if not found
                p = session.query(ESGFPermission).filter(ESGFPermission.user_id==esgfUser.id).filter(ESGFPermission.group_id==esgfGroup.id).filter(ESGFPermission.role_id==esgfRole.id).one()
                return p.approved
            
            except NoResultFound:
                return None
                            
        finally:
            session.close()
            
    def readPermissions(self, userOpenid, groupName):
        '''
        Method to read all permissions for a given user and group from the ESGF database.
        Will return an empty dictionary if no permissions are found.
        '''
        
        try:
            permissions = {}
            session = self.Session()
            
            (esgfUser, esgfGroup, _) = self._getPermissionObjects(session, userOpenid=userOpenid, groupName=groupName)
                                           
            # retrieve all existing permissions
            ps = session.query(ESGFPermission).filter(ESGFPermission.user_id==esgfUser.id).filter(ESGFPermission.group_id==esgfGroup.id)
            for p in ps:
                permissions[p.role.name] = p.approved
            return permissions
                            
        finally:
            session.close()
            
    def updatePermission(self, userOpenid, groupName, roleName, approved):
        '''
        Method to update the status of a user permission in the database.
        Will throw exception is the permission does not exist.
        '''
        
        try:
            session = self.Session()
            
            (esgfUser, esgfGroup, esgfRole) = self._getPermissionObjects(session, userOpenid=userOpenid, groupName=groupName, roleName=roleName)
                        
            # retrieve and update an existing permission
            # will throw NoResultFound if not found
            p = session.query(ESGFPermission).filter(ESGFPermission.user_id==esgfUser.id).filter(ESGFPermission.group_id==esgfGroup.id).filter(ESGFPermission.role_id==esgfRole.id).one()
            p.approved = approved 
            session.commit()
                            
        finally:
            session.close()
            
    def deletePermission(self, userOpenid, groupName, roleName, approved):
        '''
        Method to delete an existing permission from the database.
        Will throw exception is the permission does not exist.
        '''
        
        try:
            session = self.Session()
            
            (esgfUser, esgfGroup, esgfRole) = self._getPermissionObjects(session, userOpenid=userOpenid, groupName=groupName, roleName=roleName)
                        
            # retrieve and update an existing permission
            # will throw NoResultFound if not found
            p = session.query(ESGFPermission).filter(ESGFPermission.user_id==esgfUser.id).filter(ESGFPermission.group_id==esgfGroup.id).filter(ESGFPermission.role_id==esgfRole.id).one()
            p.delete()
            session.commit()
                            
        finally:
            session.close()
        
            
    def _getPermissionObjects(self, session, userOpenid=None, groupName=None, roleName=None):
        '''
        Method to retrieve the database objects used by the Permission table.
        Throws exception if the objects don't exist in the database.
        Must be used within an already established session.
        '''
        
        # retrieve user
        if userOpenid is not None:
            try:
                esgfUser = session.query(ESGFUser).filter(ESGFUser.openid==userOpenid).one()      
            except NoResultFound:
                raise Exception("User with openid=%s not found" % userOpenid)
        else:
            esgfUser = None
            
        # retrieve group
        if groupName is not None:
            try:
                esgfGroup = session.query(ESGFGroup).filter(ESGFGroup.name==groupName).one()   
            except NoResultFound:
                raise Exception("Group with name=%s not found" % groupName)
        else:
            esgfGroup = None
            
        # retrieve role
        if roleName is not None:
            try:
                esgfRole = session.query(ESGFRole).filter(ESGFRole.name==roleName).one()   
            except NoResultFound:
                raise Exception("Role with name=%s not found" % roleName)
        else:
            esgfRole = None

        return (esgfUser, esgfGroup, esgfRole)