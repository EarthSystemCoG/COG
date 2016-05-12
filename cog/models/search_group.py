from django.db import models
from constants import APPLICATION_LABEL
from search_profile import SearchProfile

# Group of search facets
class SearchGroup(models.Model):
    
    DEFAULT_NAME = 'default'
    
    profile = models.ForeignKey(SearchProfile, related_name="groups", blank=False, null=False)
    name =  models.CharField(max_length=40, null=False, blank=False, default=DEFAULT_NAME)
    order = models.IntegerField(blank=True, default=0)
    
    def size(self):
        """Returns the number of facets in the group."""
        return len(list(self.facets.all()))
    
    def __unicode__(self):
        #return "Search Group name='%s', order='%s'" % (self.name, self.order)
        return self.name
    
    class Meta:
        app_label= APPLICATION_LABEL