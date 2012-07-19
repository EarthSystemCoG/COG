from django.db import models
from constants import APPLICATION_LABEL

# A category to group Posts
class Topic(models.Model):
    
        name = models.CharField(max_length=200, verbose_name='Name', blank=False)
        description = models.TextField(verbose_name='Description', blank=True)
        
        def __unicode__(self):
            return self.name
        
        class Meta:
            app_label= APPLICATION_LABEL