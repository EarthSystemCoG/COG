from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from folder_conf import folderManager

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
    
# function to return the requested top bookmark folder for a project,
# creating it if not existing
def getTopFolder(project, name='Bookmark Folder'): # CHANGEME ?
    
    # get or create top-level folder
    folder, created = Folder.objects.get_or_create(name=name, parent=None, project=project)
    if created:
        print 'Project=%s: reated top-level folder=%s' % (project.short_name, folder.name)
    return folder

# function to return all top-level folders for a project,
# creating them if not existing
def getTopFolders(project):
    
    folders = []
    for name in folderManager.getNames():
        # get or create top-level folder
        folder, created = Folder.objects.get_or_create(name=name, parent=None, project=project)
        folders.append(folder)
        if created:
            print 'Project=%s: reated top-level folder=%s' % (project.short_name, folder.name)

    return folders