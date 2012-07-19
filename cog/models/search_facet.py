from django.db import models
from constants import APPLICATION_LABEL
from search_profile import SearchProfile

# Search facet displayed in user interface
class SearchFacet(models.Model):
    
    profile = models.ForeignKey(SearchProfile, blank=False, null=False)
    
    key =  models.CharField(max_length=20, blank=False)
    label =  models.CharField(max_length=40, blank=False)
    order = models.IntegerField(blank=True, default=0)
    
    def __unicode__(self):
        return "Search Facet key='%s', label='%s'" % (self.key, self.label)
    
    class Meta:
        app_label= APPLICATION_LABEL