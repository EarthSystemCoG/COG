from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import logging

log = logging.getLogger()

def get_upload_path(instance, filename):
    """Function to determine the upload path dynamically at runtime."""
    return os.path.join(getattr(settings, "FILEBROWSER_DIRECTORY"), str(instance.project.short_name.lower()), filename)


class OverridingFileStorage(FileSystemStorage):
    """Subclass of FileSystemStorage that overrides existing files (in the same folder)."""

    # This method is actually defined in Storage
    # note: max_length=None required as of Django 1.10:
    # see https://docs.djangoproject.com/en/1.10/releases/1.8/#support-for-the-max-length-argument-on-custom-storage-classes
    def save(self, name, content, max_length=None): 
        # must delete current file first  
        if self.exists(name):
            log.debug('Deleting existing file=%s' % name)
            self.delete(name)     
        # also, look for Doc objects for the same named file  
        prefix = getattr(settings, "FILEBROWSER_DIRECTORY", "")
        filepath = name[len(prefix):]
        docs = Doc.objects.filter(path__endswith=filepath)
        for doc in docs:
            doc.delete()
        return super(OverridingFileStorage, self).save(name, content)
  
ofs = OverridingFileStorage()


# A generic document that can be uploaded to the server and attached to a Post
class Doc(models.Model):
    
    author = models.ForeignKey(User, related_name='documents', verbose_name='Publisher', blank=False, null=True,
                               on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, blank=True)
    # path == 'file.name' but stored in the database for searching
    path = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    # upload path is obtained dynamically from the callable function
    file = models.FileField(upload_to=get_upload_path, storage=ofs, max_length=400)
    publication_date = models.DateTimeField('Date Published', auto_now_add=True)
    update_date = models.DateTimeField('Date Updated', auto_now=True)
    project = models.ForeignKey(Project)
    # public/private flag
    is_private = models.BooleanField(verbose_name='Private?', default=False, null=False)
    
    def __unicode__(self):
        if self.title: 
            return self.title 
        else:
            return os.path.basename(self.file.name)
    
    class Meta:
        app_label = APPLICATION_LABEL
