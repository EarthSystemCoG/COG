from django.db import models
from .constants import APPLICATION_LABEL
from .search_group import SearchGroup

# Search facet displayed in user interface
class SearchFacet(models.Model):
    
    group = models.ForeignKey(SearchGroup, related_name="facets", blank=False, null=True)
    
    key =  models.CharField(max_length=40, blank=False)
    label =  models.CharField(max_length=40, blank=False)
    order = models.IntegerField(blank=True, default=0)
    
    def __unicode__(self):
        return "Search Facet key='%s', label='%s' order='%s' [group: %s]" % (self.key, self.label, self.order, self.group)
    
    class Meta:
        app_label= APPLICATION_LABEL