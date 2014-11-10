'''
Class to manage Group objects in the ESGF database.

@author: cinquini
'''

from cog.plugins.esgf.objects import ESGFGroup

class GroupDAO(object):
    
    def __init__(self, Session):
        
        # session factory
        self.Session = Session
        
    def readGroups(self):
        '''
        Method to read all access control groups from the local ESGF database.
        Will return a list where each element is a dictionary encoding all the attributes of a group.
        '''
        
        try:
            groups = []
            session = self.Session()
            
            for esgfGroup in session.query(ESGFGroup).order_by(ESGFGroup.name):
                group = {}
                group['name'] = esgfGroup.name
                group['description'] = esgfGroup.description
                group['visible'] = esgfGroup.visible
                group['automatic_approval'] = esgfGroup.automatic_approval
            
                groups.append( group )
                
            return groups
                            
        finally:
            session.close()
