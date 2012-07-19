from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from django.contrib.auth.models import User
from os.path import basename

# A generic document that can be uploaded to the server and attached to a Post
class Doc(models.Model):
    
    author = models.ForeignKey(User, related_name='documents', verbose_name='Publisher', blank=False)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='docs/')
    publication_date = models.DateTimeField('Date Published', auto_now_add=True)
    update_date = models.DateTimeField('Date Updated', auto_now=True)
    project = models.ForeignKey(Project)
    
    def __unicode__(self):
        if self.title: 
            return self.title 
        else : 
            return basename(self.file.name)
    
    class Meta:
        app_label= APPLICATION_LABEL
