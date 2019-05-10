from django.db import models
from .constants import APPLICATION_LABEL
from django.contrib.auth.models import User
from .management_body import ManagementBody

class ManagementBodyMember(models.Model):
    
    user = models.ForeignKey(User, blank=False, null=False)
    managementBody = models.ForeignKey(ManagementBody, blank=False, null=False)
            
    class Meta:
        unique_together = (("user", "managementBody"),)    
        app_label = APPLICATION_LABEL
