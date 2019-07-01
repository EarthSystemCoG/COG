from django.db import models
from .constants import APPLICATION_LABEL
from .project import Project

# Project-specific search configuration (persisted to the database)
class SearchProfile(models.Model):
    
    project = models.OneToOneField(Project, blank=False, null=False, on_delete=models.CASCADE)
    
    # name that identifies this configuration
    #name = models.CharField(max_length=50, blank=False, unique=True, default='')
    
    # The URL of the back-end search service - don't verify its existence because it might take longer than allowed
    url = models.URLField(blank=False)
        
    # string of the form name=value, name=value....
    constraints = models.CharField(max_length=500, blank=True, null=True, default='')
    
    # flag to enable model metadata link
    modelMetadataFlag = models.BooleanField(default=False, blank=False, null=False)
    
    # flag to display replicas checkbox
    replicaSearchFlag = models.BooleanField(default=False, blank=False, null=False)
    
    # flag to display versions checkbox
    latestSearchFlag = models.BooleanField(default=False, blank=False, null=False)

    # flag to display local search checkbox
    localSearchFlag = models.BooleanField(default=False, blank=False, null=False)
    
    # help text to describe this project's search capabilities
    description = models.TextField(blank=True, null=True, verbose_name='Search Help', help_text='Optional description of this project search capabilities.')
    
    def facets(self):
        """ Method to return a list of facets, across all groups."""
        
        facets = []
        for group in self.groups.all():
            facets = facets + list( group.facets.all() )
        return facets
    
    def __unicode__(self):
        return "%s Search Profile" % self.project.short_name
    
    class Meta:
        app_label= APPLICATION_LABEL
