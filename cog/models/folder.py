from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from folder_conf import folderManager
from collections import OrderedDict

# dictionary of pre-defined (folder key, folder name)
TOP_FOLDERS = OrderedDict([ ('RESOURCES', 'Bookmarks'), # overall parent
                            ('PRESENTATIONS', 'Presentations'), 
                            ('PUBLICATIONS', 'Publications'),
                            ('NEWSLETTERS', 'Newsletters'),
                            ('PROPOSALS', 'Proposals'),
                            ('FIGURES', 'Figures'),
                            ('TESTCASES', 'Test Cases'),
                            ('EVALUATIONS', 'Evaluations') ])

class Folder(models.Model):
    
    project = models.ForeignKey(Project, blank=False)
    name =  models.CharField(max_length=200, blank=False)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='Parent Folder')
    active = models.BooleanField(default=True, blank=False, null=False)
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
        unique_together = (("project", "name"),)
        app_label= APPLICATION_LABEL
    
def getTopFolder(project):
    ''' Function to return the top bookmarks folder for a project, creating it if not existing.'''
    
    # get or create top-level folder
    name = "%s %s" % (project.short_name, TOP_FOLDERS['RESOURCES'])
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