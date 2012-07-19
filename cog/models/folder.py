from django.db import models
from constants import APPLICATION_LABEL
from project import Project

class Folder(models.Model):
    
    project = models.ForeignKey(Project, blank=False)
    name =  models.CharField(max_length=200, blank=False)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='Parent Folder')
    order = models.IntegerField(blank=True, default=0)
    
    def __unicode__(self):
        return self.name
   
    def children(self):
        return Folder.objects.filter(parent=self).order_by('order')

    class Meta:
        app_label= APPLICATION_LABEL
    
# function to return the top bookmark folder for a project
def getTopFolder(project):
    
    name = "%s Bookmarks" % project.short_name
    # get or create top-level folder
    folder, created = Folder.objects.get_or_create(name=name, parent=None, project=project)
    return folder