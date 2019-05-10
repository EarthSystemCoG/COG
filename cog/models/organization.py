from django.db import models
from .constants import APPLICATION_LABEL, UPLOAD_DIR_LOGOS
from .project import Project


class Organization(models.Model):
    
    name = models.CharField(max_length=200, blank=False, help_text='Project or organization that collaborates on this project')
    url = models.URLField(max_length=200, blank=True, null=True, help_text='Organization URL')
    image = models.ImageField(upload_to=UPLOAD_DIR_LOGOS, blank=True, null=True)
    project = models.ForeignKey(Project, blank=False)
    
    def __unicode__(self):
        return "Project=%s Organization=%s" % (self.project, self.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
