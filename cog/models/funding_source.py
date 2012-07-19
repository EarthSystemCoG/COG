from django.db import models
from constants import APPLICATION_LABEL
from project import Project

class FundingSource(models.Model):
    name = models.CharField(max_length=200, blank=False, help_text='Organization or agency that financially supports the project')
    project = models.ForeignKey(Project, blank=False)
    
    def __unicode__(self):
        return "Project=%s Funding Source=%s" % (self.project, self.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
