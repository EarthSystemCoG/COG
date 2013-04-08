from django.db import models
from constants import APPLICATION_LABEL
from cog.models import UserProfile

class UserUrl(models.Model):   
    '''Class representing user-defined URLs references, part of the user profile.'''
    
    url = models.URLField('URL', blank=False, null=False, verify_exists=False, max_length=1000)
    name =  models.CharField(max_length=200, blank=False, null=False)
    profile = models.ForeignKey(UserProfile, blank=False, null=False)
    
    class Meta:
        app_label= APPLICATION_LABEL
