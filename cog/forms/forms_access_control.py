'''
Module containing forms for access control management.

@author: cinquini
'''

from django.forms import (Form, BooleanField)
from cog.plugins.esgf.objects import ROLE_USER, ROLE_PUBLISHER, ROLE_SUPERUSER, ROLE_ADMIN

class PermissionForm(Form):
    
    # required=False because if checkbox is NOT checked no value is passed in the POST data
    userPermissionCheckbox = BooleanField(required=False, label=ROLE_USER.capitalize())
    publisherPermissionCheckbox = BooleanField(required=False, label=ROLE_PUBLISHER.capitalize())
    adminPermissionCheckbox = BooleanField(required=False, label=ROLE_ADMIN.capitalize())
    superPermissionCheckbox = BooleanField(required=False, label=ROLE_SUPERUSER.capitalize())