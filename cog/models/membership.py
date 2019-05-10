from django.db import models
from .constants import APPLICATION_LABEL
from django.contrib.auth.models import User, Group
import django.dispatch

# Object holding user requests to join a group
class MembershipRequest(models.Model):
    
    user = models.ForeignKey(User)    
    group = models.ForeignKey(Group)   
    date = models.DateTimeField('Request Date', auto_now=True)

    class Meta:
        unique_together = (("user", "group"),)
        app_label = APPLICATION_LABEL

