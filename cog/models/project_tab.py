from django.db import models
from .constants import APPLICATION_LABEL
from .navbar import PROJECT_PAGES, DEFAULT_TABS
from .project import Project
from django.core.urlresolvers import reverse
from cog.models.dbutils import UnsavedForeignKey

    
# Tab displayed in project top navigation menu
class ProjectTab(models.Model):
        
    project = UnsavedForeignKey(Project, blank=False, null=False, related_name="tabs")
    
    # the URL of a corresponding project page
    url = models.CharField(max_length=200, verbose_name='URL', blank=True, unique=True, default='')
    # the label displayed in the menu
    label =  models.CharField(max_length=40, blank=False, null=False)
    # whether or not the tab will be displayed
    active = models.BooleanField(default=True, null=False, blank=False)
    # optional parent tab (null for top-level tabs)
    parent = models.ForeignKey('self', blank=True, null=True)
    
    def __unicode__(self):
        return "Project Tab label='%s', url='%s', active=%s" % (self.label, self.url, self.active)
    
    def suburl(self):
        # returns the last part of the tab URL: url='/projects/climatetranslator/metrics/' --> 'metrics'
        return self.url.split('/')[-2]
    
    class Meta:
        app_label= APPLICATION_LABEL