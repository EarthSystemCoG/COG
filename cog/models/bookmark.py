from django.db import models
from .constants import APPLICATION_LABEL
from cog.models import Post


class Bookmark(models.Model):   
    
    url = models.URLField('URL', blank=False, max_length=1000)
    name = models.CharField(max_length=1000, blank=False)
    folder = models.ForeignKey('Folder', blank=False, null=False)
    description = models.TextField(max_length=1000, blank=True, null=True)
    order = models.IntegerField(blank=True, default=0)
    # note: do not delete bookmark if notes is deleted
    notes = models.ForeignKey(Post, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return "%s [%s]" % (self.name, self.url)

    class Meta:
        app_label = APPLICATION_LABEL
        
    # method to assign a Notes object
    def setPost(self, post):
        self.notes = post