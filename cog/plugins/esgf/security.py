from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from passlib.hash import md5_crypt
from uuid import uuid4
from django_openid_auth.models import UserOpenID

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
            metadata = Base.metadata

            # session factory
            self.Session = sessionmaker(bind=engine)
            
    def createOpenid(self, userProfile):
        '''Selects the first available ESGF openid starting from the CoG username, and saves it in the CoG database'''
        
        openid = ESGF_OPENID_TEMPLATE.replace("<ESGF_HOSTNAME>", settings.ESGF_HOSTNAME).replace("<ESGF_USERNAME>", userProfile.user.username)        
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
                    print 'Added openid=%s for user=%s into COG database' % (_openid, userProfile.user)
                    return userOpenID.claimed_id
                
        finally:
            session.close()
            
        return None # openid not assigned
        
        
            
    def insertUser(self, userProfile):
        
        # use existing local openid...
        _openid = userProfile.localOpenid()
        
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
            session.close()
            return esgfUser
        
        except NoResultFound:
            return None
        
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
            


Base = declarative_base()
class ESGFUser(Base):
    """ Class that represents the 'esgf_secitity.user' table in the ESGF database."""

    __tablename__ = 'user'
    #__table_args__ = { 'autoload':True, 'schema':'esgf_security' }
    __table_args__ = { 'schema':'esgf_security' }

    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    middlename = Column(String)
    lastname = Column(String)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    dn = Column(String)
    openid = Column(String)
    organization = Column(String)
    organization_type = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    status_code = Column(Integer)
    verification_token = Column(String)
    notification_code = Column(Integer)

esgfDatabaseManager = ESGFDatabaseManager()