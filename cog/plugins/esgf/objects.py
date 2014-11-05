'''
Module containing python objects matching the ESGF database tables.
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

ROLE_USER = 'user'
ROLE_PUBLISHER = 'publisher'
ROLE_ADMIN = 'admin'
ROLE_SUPERUSER = 'super'

class ESGFUser(Base):
    """ Class that represents the 'esgf_security.user' table in the ESGF database."""

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


class ESGFGroup(Base):
    """ Class that represents the 'esgf_secitity.group' table in the ESGF database."""

    __tablename__ = 'group'
    __table_args__ = { 'schema':'esgf_security' }
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    visible = Column(Boolean)
    automatic_approval = Column(Boolean)
    
    
class ESGFRole(Base):
    """ Class that represents the 'esgf_security.role' table in the ESGF database."""

    __tablename__ = 'role'
    __table_args__ = { 'schema':'esgf_security' }
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    
    
class ESGFPermission(Base):
    """ Class that represents the 'esgf_security.permission' table in the ESGF database."""
    
    __tablename__ = 'permission'
    __table_args__ = { 'schema':'esgf_security' }
    
    user_id = Column(Integer, ForeignKey('esgf_security.user.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('esgf_security.group.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('esgf_security.role.id'), primary_key=True)
    approved = Column(Boolean)
    
    user = relationship("ESGFUser")
    group = relationship("ESGFGroup")
    role = relationship("ESGFRole")
