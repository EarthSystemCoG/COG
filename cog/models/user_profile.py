from django.db import models
from django.contrib.auth.models import Group, Permission, User, Group
from constants import APPLICATION_LABEL

class UserProfile(models.Model):
    
    # user
    user = models.OneToOneField(User)
        
    # additional mandatory fields
    institution = models.CharField(max_length=100, blank=False, default='')
    city = models.CharField(max_length=100, blank=False, null=False, default='')
    country = models.CharField(max_length=100, blank=False, null=False, default='')
    
    # additional optional fields
    state = models.CharField(max_length=100, blank=True, null=True, default='')
    department = models.CharField(max_length=100, blank=True, null=True, default='')
    
    # opt-in mailing list (but defaults to true to migrate existing users)
    subscribed = models.BooleanField(verbose_name='Subscribe to COG mailing list ?', default=True, null=False)
    
    # opt-out privacy option
    private = models.BooleanField(verbose_name='Do NOT list me among project members', default=False, null=False)
    
    # optional picture
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    
    class Meta:
        app_label= APPLICATION_LABEL

# NOTE: monkey-patch User __unicode__() method to show full name
User.__unicode__ = User.get_full_name