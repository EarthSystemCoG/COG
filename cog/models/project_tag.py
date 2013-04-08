from django.db import models
from constants import APPLICATION_LABEL

class ProjectTag(models.Model):
        
    name = models.CharField(max_length=200, blank=False, null=False, unique=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label= APPLICATION_LABEL