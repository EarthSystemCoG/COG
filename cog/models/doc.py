from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from django.contrib.auth.models import User
import os
from django.conf import settings

# function to determine the upload path dynamically at runtime
def get_upload_path(instance, filename):
    return os.path.join(getattr(settings, "FILEBROWSER_DIRECTORY"), str(instance.project.short_name.lower()), filename)

# A generic document that can be uploaded to the server and attached to a Post
class Doc(models.Model):
    
    author = models.ForeignKey(User, related_name='documents', verbose_name='Publisher', blank=False)
    title = models.CharField(max_length=200, blank=True)
    # path == 'file.name' but stored in the database for searching
    path = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    # upload path is obtained dynamically from the callable function
    file = models.FileField(upload_to=get_upload_path)
    publication_date = models.DateTimeField('Date Published', auto_now_add=True)
    update_date = models.DateTimeField('Date Updated', auto_now=True)
    project = models.ForeignKey(Project)
    # public/private flag
    is_private = models.BooleanField(verbose_name='Private ?', default=False, null=False)
    
    def __unicode__(self):
        if self.title: 
            return self.title 
        else:
            return os.path.basename(self.file.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
