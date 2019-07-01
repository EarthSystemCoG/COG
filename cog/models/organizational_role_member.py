from django.db import models
from .constants import APPLICATION_LABEL
from django.contrib.auth.models import User
from .organizational_role import OrganizationalRole

class OrganizationalRoleMember(models.Model):
    
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    organizationalRole = models.ForeignKey(OrganizationalRole, blank=False, null=False, on_delete=models.CASCADE)
            
    class Meta:
        unique_together = (("user", "organizationalRole"),)    
        app_label = APPLICATION_LABEL
