'''
Service for managing registration of users in access control groups.

@author: Luca Cinquini
'''

import abc

class RegistrationService(object):
    
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def createGroup(self, name, description='', visible=True, automatic_approval=False):
        '''
        Method used by system administrators to create an access control group.
        
        :param name: the group name
        :type name: string
        :param description: the group description
        :type description: string
        :param visible: True if the group is advertised to the public, False otherwise
        :type visible: boolean
        :param automatic_approval: True if users are automatically approved, False if users must be approved by an administrator
        :type automatic_approval: boolean
        
        :returns: the operation outcome: 'created' if a new group was created, 'exsiting' if it already existed
        :rtype: string
        '''
        
        pass

    @abc.abstractmethod
    def subscribe(self, userOpenid, groupName, roleName):
        '''
        User method to apply for membership in a group with a given role.
        If the permission does not exist, it will be created and its status will be returned.
        If the permission already exists, its current status will be returned.
        
        :param userOpenid: the user openid (must exist)
        :type userOpenid: string
        :param groupName: the group name (must exist)
        :type groupName: string
        :param roleName: the role name (must exist)
        :type roleName: string

        :returns: the permission approved status: True if the membership was granted, False if the membership is waiting for approval.
        :rtype: boolean
        
        '''
        
        return False
    
    @abc.abstractmethod
    def process(self, userOpenid, groupName, roleName, approve):
        '''
        Administrator method to approve or reject a user subscription.
        If the permission does not exist, an exception will be thrown.
        
        :param userOpenid: the user openid (must exist)
        :type userOpenid: string
        :param groupName: the group name (must exist)
        :type groupName: string
        :param roleName: the role name (must exist)
        :type roleName: string
        :param approve: True to approve the permission, False to reject it
        "type approve: boolean
        
        '''
        
        return
    
    @abc.abstractmethod
    def status(self, userOpenid, groupName, roleName):
        '''
        Method to retrieve the approval status of a user permission.
        If the permission does not exist, None will be returned.
        
        :param userOpenid: the user openid (must exist)
        :type userOpenid: string
        :param groupName: the group name (must exist)
        :type groupName: string
        :param roleName: the role name (must exist)
        :type roleName: string

        :returns: the permission approved status: True if the membership was granted, False if the membership is waiting for approval.
        :rtype: boolean
        
        '''
        
        return False
    
    @abc.abstractmethod
    def list(self, userOpenid, groupName):
        '''
        Method to list all permissions for a given user and group.
        
        :param userOpenid: the user openid (must exist)
        :type userOpenid: string
        :param groupName: the group name (must exist)
        :type groupName: string

        :returns: a dictionary containing the roles as keys, the corresponding boolean approved status as values 
                  (or None if that permission does not exist)
        :rtype: (string, boolean) dictionary
        
        '''
        
        return {}