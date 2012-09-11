from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from django.contrib.auth.models import User
import os

# function to determine the upload path dynamically at runtime
def get_upload_path(instance, filename):
    return os.path.join('docs/', str(instance.project.short_name), filename)

# A generic document that can be uploaded to the server and attached to a Post
class Doc(models.Model):
    
    author = models.ForeignKey(User, related_name='documents', verbose_name='Publisher', blank=False)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # upload path is obtained dynamically from the callable function
    file = models.FileField(upload_to=get_upload_path)
    publication_date = models.DateTimeField('Date Published', auto_now_add=True)
    update_date = models.DateTimeField('Date Updated', auto_now=True)
    project = models.ForeignKey(Project)
    
    def __unicode__(self):
        if self.title: 
            return self.title 
        else : 
            return os.basename(self.file.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
