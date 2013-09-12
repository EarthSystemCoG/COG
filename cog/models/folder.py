from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from project_tab import ProjectTab
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
    
    def topParent(self):
        '''Returns the top-level parent of this folder.'''
        
        if self.parent==None:
            return self
        else:
            return self.parent.topParent() # recursion

    class Meta:
        app_label= APPLICATION_LABEL
    
# function to return the requested top bookmark folder for a project,
# creating it if not existing
def getTopFolder(project, name=folderManager.getFolderName('RESOURCES')):
    
    # get or create top-level folder
    folder, created = Folder.objects.get_or_create(name=name, parent=None, project=project)
    if created:
        print 'Project=%s: created top-level folder=%s' % (project.short_name, folder.name)
    return folder

# function to return all top-level folders for a project,
# creating them if not existing
def getTopFolders(project):
    
    folders = []
    for name in folderManager.getFolderNames():
        # get or create top-level folder
        folder, created = Folder.objects.get_or_create(name=name, parent=None, project=project)
        folders.append(folder)
        if created:
            print 'Project=%s: created top-level folder=%s' % (project.short_name, folder.name)

    return folders

def getActiveFolders(project):
    '''Returns a list of active folders for this project (both top-level and nested) .'''
    
    # list of existing folders for this project
    folders = Folder.objects.filter(project=project)
        
    # list of active project tabs
    tabs = ProjectTab.objects.filter(project=project, active=True)
    
    # select active folders
    activeFolders = []
    for folder in folders:
        # use the top-level parent
        topFolder = folder.topParent()
        suburl = folderManager.getFolderSubUrlFromName(topFolder.name)
        for tab in tabs:
            # example: 'resources' in '/projects/abc123/resources/'
            if suburl in tab.url: 
                activeFolders.append(folder)
                break
            
    return activeFolders