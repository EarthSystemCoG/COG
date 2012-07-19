from django.db import models
from constants import APPLICATION_LABEL
from project import Project


class Organization(models.Model):
    name = models.CharField(max_length=200, blank=False, help_text='Project or organization that collaborates on this project')
    project = models.ForeignKey(Project, blank=False)
    
    def __unicode__(self):
        return "Project=%s Organization=%s" % (self.project, self.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
