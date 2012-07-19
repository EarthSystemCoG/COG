from django.db import models
from constants import APPLICATION_LABEL
from django.contrib.auth.models import User
from project import Project

# A piece of News about a Project
class News(models.Model):
    
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User)
    publication_date = models.DateTimeField('Date Published', auto_now_add=True)
    update_date = models.DateTimeField('Date Updated', auto_now=True)
    project = models.ForeignKey(Project, verbose_name='About Project')
    other_projects = models.ManyToManyField(Project, verbose_name='Projects Notified', related_name='other_news', blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        app_label= APPLICATION_LABEL