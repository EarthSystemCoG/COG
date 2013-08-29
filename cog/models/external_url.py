from django.db import models
from constants import APPLICATION_LABEL
from external_url_page import external_url_choices
from project import Project

# A reference to an external URL
class ExternalUrl(models.Model):
        
    title = models.CharField(max_length=200, verbose_name='Title', blank=False)
    description = models.CharField(max_length=1000, blank=True)
    url = models.URLField('URL', blank=False, max_length=1000)
    type = models.CharField(max_length=20, verbose_name='URL Type', blank=False, choices=external_url_choices())
    project = models.ForeignKey(Project)
    
    def __unicode__(self):
        return "URL Type=%s Title='%s' url='%s' description='%s'" % (self.type, self.title, self.url, self.description)
    
    class Meta:
        app_label= APPLICATION_LABEL