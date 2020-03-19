from django.db import models
from .constants import APPLICATION_LABEL, UPLOAD_DIR_LOGOS
from .project import Project

class FundingSource(models.Model):
    
    name = models.CharField(max_length=200, blank=False, help_text='Organization or agency that financially supports the project')
    url = models.URLField(max_length=200, blank=True, null=True, help_text='Funding Source URL')
    image = models.ImageField(upload_to=UPLOAD_DIR_LOGOS, blank=True, null=True)
    project = models.ForeignKey(Project, blank=False, on_delete=models.CASCADE)
    
    def __unicode__(self):
        return "Project=%s Funding Source=%s" % (self.project, self.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
