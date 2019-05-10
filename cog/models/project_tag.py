from django.db import models
from .constants import APPLICATION_LABEL

MAX_PROJECT_TAG_LENGTH = 20


class ProjectTag(models.Model):
        
    name = models.CharField(max_length=MAX_PROJECT_TAG_LENGTH, blank=True, null=False, unique=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label= APPLICATION_LABEL