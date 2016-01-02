from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from passlib.hash import md5_crypt
from uuid import uuid4
from django_openid_auth.models import UserOpenID


from cog.plugins.esgf.objects import ESGFGroup, ESGFRole, ESGFUser, ESGFPermission
from cog.plugins.esgf.permissionDAO import PermissionDAO
from cog.plugins.esgf.groupDao import GroupDAO

from django.conf import settings

OPENID_EXTENSIONS = [""] + [str(i) for i in range(1,100)]
ESGF_OPENID_TEMPLATE="https://<ESGF_HOSTNAME>/esgf-idp/openid/<ESGF_USERNAME>"

class ESGFDatabaseManager():
    '''Class that manages connections to the ESGF database.'''

    def __init__(self):
        '''Constructor establishes a connection pool to the ESGF database,
        from the configuration parameters contained in cog_settings.cfg'''

        #if os.getenv('DJANGO_SETTINGS_MODULE', None) and settings.ESGF_CONFIG:
        if settings.ESGF_CONFIG:

            #siteManager = SiteManager()
            self._hostname = settings.ESGF_HOSTNAME
            dburl = settings.ESGF_DBURL

            #engine = create_engine('postgresql://DBUSERNAME:DBPASSWORD@localhost/esgcet', echo=False)
            engine = create_engine(dburl, echo=False)
            #metadata = Base.metadata

            # session factory
            self.Session = sessionmaker(bind=engine)
            
            # DAOs
            self.groupDao = GroupDAO(self.Session)
            self.permissionDao = PermissionDAO(self.Session)
            
    def buildOpenid(self, username):
        '''Builds an ESGF openid from a given username.'''
        return ESGF_OPENID_TEMPLATE.replace("<ESGF_HOSTNAME>", settings.ESGF_HOSTNAME).replace("<ESGF_USERNAME>", username)        
        
        
    def createOpenid(self, userProfile):
        '''Selects the first available ESGF openid starting from the CoG username, and saves it in the CoG database'''
        
        openid = self.buildOpenid(userProfile.user.username)
        session = self.Session()
        
        try:
            
            # try N times
            for ext in OPENID_EXTENSIONS:
                _openid = openid + ext
                try:
                    result = session.query(ESGFUser).filter(ESGFUser.openid==_openid).one()
                    print 'User with openid=%s already exists, trying another one' % _openid
    
                except MultipleResultsFound:
                    # problem in ESGF database, but ignore here
                    print 'Warning: found multiple users with openid=%s' % _openid
    
                except NoResultFound:    
                    # this openid is available
                    userOpenID = UserOpenID.objects.create(user=userProfile.user, claimed_id=_openid, display_id=_openid)
                    print 'Added openid=%s for user=%s into COG database' % (_openid, userProfile.user.username)
                    return userOpenID.claimed_id
                
        finally:
            session.close()
            
        return None # openid not assigned
    
    def checkOpenid(self, openid):
        '''Returns true if the given openid exists in the ESGF database, false otherwise.'''
        
        session = self.Session()
        try:
            
            if session.query(ESGFUser).filter(ESGFUser.openid==openid).first() is not None:
                return True
            else:
                return False
            
        finally:
            session.close()

        
    def createGroup(self, name, description='', visible=True, automatic_approval=False):
        
        created = False
        
        try:
            session = self.Session()
            
            group = session.query(ESGFGroup).filter( func.lower(ESGFGroup.name) == func.lower(name) ).one()
            print "Group with name=%s already exists" % group.name
            created = False
            
            return group
            
        except NoResultFound:
            group = ESGFGroup(name=name, description=description, visible=visible, automatic_approval=automatic_approval)
            session.add(group)
            session.commit()
            created = True
            
            return group
            
        finally:
            session.close()
        
        return created
            
    def insertUser(self, userProfile):
        
        # use existing openid...
        _openid = userProfile.openid()
        #_openid = userProfile.localOpenid()
        
        # ...or create new local openid and insert into CoG database
        if _openid is None:
            _openid = self.createOpenid(userProfile)

        # do NOT override ESGF database
        esgfUser = self.getUserByOpenid(_openid)

        if esgfUser is None:
            
            session = self.Session()
    
            try:
                
                # encrypt password with MD5_CRYPT
                clearTextPassword = userProfile.clearTextPassword
                if clearTextPassword is not None and len(clearTextPassword)>0:
                    encPassword = md5_crypt.encrypt(clearTextPassword)
                else:
                    encPassword = None
    
                _username = _openid[ _openid.rfind('/')+1: ]
                esgfUser = ESGFUser(firstname=userProfile.user.first_name, lastname=userProfile.user.last_name,
                                    email=userProfile.user.email, username=_username, password=encPassword,
                                    dn='', openid=_openid, organization=userProfile.institution, organization_type='',
                                    city=userProfile.city, state=userProfile.state, country=userProfile.country,
                                    status_code=1, verification_token=str(uuid4()), notification_code=0)
    
                session.add(esgfUser)
                session.commit()
                print 'Inserted user with openid=%s into ESGF database' % _openid
    
            finally:
                session.close()

        else:
            #print 'User with openid: %s already existing in ESGF database, no action taken' % esgfUser.openid
            pass
            
        return esgfUser

    def getUserByOpenid(self, openid):
        '''Retrieves a user by the unique openid value.'''

        try:
            session = self.Session()
            esgfUser = session.query(ESGFUser).filter(ESGFUser.openid==openid).one()        
            return esgfUser
        
        except NoResultFound:
            return None
        
        finally:
            session.close()
            
    def getGroup(self, name):
        '''Retrieves a group by name.'''
        
        try:
            session = self.Session()
            esgfGroup = session.query(ESGFGroup).filter(ESGFGroup.name==name).one()        
            return esgfGroup
        
        except NoResultFound:
            return None
        
        finally:
            session.close()
            
    def getRole(self, name):
        '''Retrieves a role by name.'''
        
        try:
            session = self.Session()
            esgfRole = session.query(ESGFRole).filter(ESGFRole.name==name).one()        
            return esgfRole
        
        except NoResultFound:
            return None
        
        finally:
            session.close()            
        
    def listUsers(self):
        
        session = self.Session()
        users = session.query(ESGFUser)
        
        for user in users:
            parts = user.openid.split('/')
            new_username = parts[-1]
            print 'Updating user: openid=%s new username=%s' % (user.openid, new_username)
            user.username = new_username
            
        session.commit()
        session.close()
        
    def listGroups(self):
        
        session = self.Session()
        groups = session.query(ESGFGroup)
        session.close()
        
        return groups
        
    def listRoles(self):
        
        session = self.Session()
        roles = session.query(ESGFRole)
        session.close()
        
        return roles
        
    
    def getUsersByEmail(self, email):
        '''Retrieves a list of users with a given email address.'''

        session = self.Session()
        esgfUsers = session.query(ESGFUser).filter(ESGFUser.email==email).all()
        session.close()
        return esgfUsers
    
    def updatePassword(self, user, clearTextPassword):
        '''Updates the user password in the ESGF database.'''
                
        for openid in user.profile.openids():
            
            # openid must match the configured ESGF host name
            if settings.ESGF_HOSTNAME in openid:
                
                esgfUser = self.getUserByOpenid(openid)
                if esgfUser is not None:
                    session = self.Session()
                    encPasword = md5_crypt.encrypt(clearTextPassword)
                    esgfUser.password = encPasword
                    print 'Updated ESGF password for user with openid: %s' % openid
                    session.add(esgfUser)
                    session.commit()
                    session.close()
                    
    def updateUser(self, user_profile):
        '''Updates the user data in the ESGF database.'''
                
        for openid in user_profile.openids():
            
            # openid must match the configured ESGF host name
            if settings.ESGF_HOSTNAME in openid:
                esgfUser = self.getUserByOpenid(openid)
                if esgfUser is not None:
                    session = self.Session()
                    esgfUser.firstname = user_profile.user.first_name
                    esgfUser.lastname = user_profile.user.last_name
                    esgfUser.email = user_profile.user.email
                    #esgfUser.username # ESGF username may be different than CoG username
                    esgfUser.organization = user_profile.institution
                    esgfUser.city = user_profile.city
                    esgfUser.state = user_profile.state
                    esgfUser.country = user_profile.country
                    print 'Updated ESGF data for user with openid: %s' % openid
                    session.add(esgfUser)
                    session.commit()
                    session.close()
                    
    def deleteUser(self, user):
        '''Deletes the user from the ESGF database.'''
                
        for openid in user.profile.openids():
            # openid must match the configured ESGF host name
            if settings.ESGF_HOSTNAME in openid:
                esgfUser = self.getUserByOpenid(openid)
                
                if esgfUser is not None:
                    print 'Deleting ESGF user with openid=%s' % openid    
                    session = self.Session()
                    # delete user permissions
                    permissions = session.query(ESGFPermission).filter(ESGFPermission.user_id==esgfUser.id)
                    for p in permissions:
                        session.delete(p)
                    # delete user
                    session.delete(esgfUser)
                    session.commit()
                    session.close()    
                    
esgfDatabaseManager = ESGFDatabaseManager()