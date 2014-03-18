from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from passlib.hash import md5_crypt
import os
import sys

from django.conf import settings

OPENID_EXTENSIONS = [""] + [str(i) for i in range(1,100)]

class ESGFDatabaseManager():
    '''Class that manages connections to the ESGF database.'''

    def __init__(self):
        '''Constructor establishes a connection pool to the ESGF database,
        from the configuration parameters contained in cog_settings.cfg'''

        if os.getenv('DJANGO_SETTINGS_MODULE', None):

            #siteManager = SiteManager()
            self._hostname = settings.ESGF_HOSTNAME
            dburl = settings.ESGF_DBURL

            #engine = create_engine('postgresql://DBUSERNAME:DBPASSWORD@localhost/esgcet', echo=False)
            engine = create_engine(dburl, echo=False)
            metadata = Base.metadata

            # session factory
            self.Session = sessionmaker(bind=engine)

    def insertUser(self, firstname, middlename, lastname, email, username, password):

        session = self.Session()

        # create openid
        for ext in OPENID_EXTENSIONS:

            openid = 'https://%s/esgf-idp/openid/%s%s' % (self._hostname, username, ext)
            try:
                result = session.query(ESGFUser).filter(ESGFUser.openid==openid).one()
                print 'User with openid=%s already exist, trying another one' % result.openid

            except MultipleResultsFound:

                print 'Warning: found multiple users with openid=%s' % openid

            except NoResultFound:

                # encrypt password with MD5_CRYPT
                encPassword = md5_crypt.encrypt(password)
                #test = md5_crypt.verify(password, encPassword)

                esgfUser = ESGFUser(firstname=firstname, middlename=middlename, lastname=lastname, email=email, username=username, password=encPassword, openid=openid)
                session.add(esgfUser)
                session.commit()

                print 'Inserted user with openid=%s' % openid
                return esgfUser

        session.close()

        return None

    def getUserByOpenid(self, openid):
        '''Retrieves a user by the unique openid value.'''

        session = self.Session()
        esgfUser = session.query(ESGFUser).filter(ESGFUser.openid==openid).scalar()
        session.close()
        return esgfUser


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

if __name__ == "__main__":

    # must identify location of COG settings.py file
    import cog
    path = os.path.dirname(cog.__file__)
    sys.path.append( path )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    # insert given user
    esgfDatabaseManager = ESGFDatabaseManager()
    esgfUser = esgfDatabaseManager.insertUser('Test', 'T', 'User', 'testuser@test.com', 'testuser', 'abc123')

    # verify user was inserted
    esgfUser2 = esgfDatabaseManager.getUserByOpenid( esgfUser.openid )
    print "Retrieved user with openid=%s" % esgfUser2.openid