from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from collections import OrderedDict
from cog.models.dbutils import UnsavedForeignKey

import logging

log = logging.getLogger()

# name of project top-folder
TOP_FOLDER = "Bookmarks"

# dictionary of pre-defined (folder key, folder name)
TOP_SUB_FOLDERS = OrderedDict([('PRESENTATIONS', 'Presentations'),
                               ('PUBLICATIONS', 'Publications'),
                               ('MINUTES', 'Minutes'),
                               ('NEWSLETTERS', 'Newsletters'),
                               ('PROPOSALS', 'Proposals'),
                               ('FIGURES', 'Figures'),
                               ('TESTCASES', 'Test Cases'),
                               ('EVALUATIONS', 'Evaluations')])


class Folder(models.Model):

    project = UnsavedForeignKey(Project, blank=False)
    
    name = models.CharField(max_length=200, blank=False)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='parent_folder')
    active = models.BooleanField(default=True, blank=False, null=False)
    order = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.name

    def children(self):
        """
        NOTE: returns ONLY to active children.
        """
        return Folder.objects.filter(parent=self, active=True).order_by('order')

    def topParent(self):
        """
        Returns the top-level parent of this folder.
        """

        if self.parent is None:
            return self
        else:
            return self.parent.topParent()  # recursion

    def isPredefined(self):
        return self.parent is None or self.name in TOP_SUB_FOLDERS.values()

    class Meta:
        unique_together = (("project", "name"),)
        app_label = APPLICATION_LABEL


def getTopFolder(project):
    """
    Function to return the top bookmarks folder for a project, creating it if not existing.
    """

    # get or create top-level folder
    # name = "%s %s" % (project.short_name, TOP_FOLDER)
    folder, created = Folder.objects.get_or_create(name=TOP_FOLDER, parent=None, project=project, active=True)
    if created:
        log.debug('Project=%s: created Top-Level folder=%s' % (project.short_name, folder.name))
    return folder


def getTopSubFolders(project):
    """
    Function to return the pre-defined level-1 sub-folders for a project.
    """

    # get or create level-0 folder
    topFolder = getTopFolder(project)

    # get all direct child folders
    folders = Folder.objects.filter(parent=topFolder)
    _folders = []
    # select pre-defined folders
    for folder in folders:
        if folder.name in TOP_SUB_FOLDERS.values():
            _folders.append(folder)

    return _folders