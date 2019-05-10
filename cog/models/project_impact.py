from django.db import models
from .constants import APPLICATION_LABEL
from .project import Project

class ProjectImpact(models.Model):
    
    project = models.ForeignKey(Project, blank=False, related_name='impacts')
    title = models.CharField(max_length=200, help_text='Title for this impact.', blank=False, null=False, default='')
    description = models.TextField(blank=False, null=False, verbose_name='Project Impact', help_text='Describe a major impact of this project in its field.')
    # IMPORTANT: NEVER USE A DEFAULT WITH A FORMSET, OTHERWISE has_changed=True for empty forms!
    order = models.IntegerField(blank=True)
    
    def __unicode__(self):
        return self.description
   
    class Meta:
        app_label= APPLICATION_LABEL