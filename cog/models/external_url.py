from django.db import models
from constants import APPLICATION_LABEL, EXTERNAL_URL_TYPES
from project import Project

# A reference to an external URL
class ExternalUrl(models.Model):
        
    title = models.CharField(max_length=200, verbose_name='Title', blank=False)
    description = models.CharField(max_length=1000, blank=True)
    url = models.URLField('URL', blank=False, verify_exists=False, max_length=1000)
    type = models.CharField(max_length=20, verbose_name='URL Type', blank=False, choices=EXTERNAL_URL_TYPES)
    project = models.ForeignKey(Project)
    
    def __unicode__(self):
        return "URL Type=%s Title='%s' url='%s' description='%s'" % (self.type, self.title, self.url, self.description)
    
    class Meta:
        app_label= APPLICATION_LABEL