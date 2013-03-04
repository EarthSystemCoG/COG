from django.db import models
from constants import APPLICATION_LABEL
from project import Project

class Collaborator(models.Model):
    
    first_name = models.CharField(max_length=100, blank=False, default='')
    last_name = models.CharField(max_length=100, blank=False, default='')
    institution = models.CharField(max_length=100, blank=False, default='')
    project = models.ForeignKey(Project, blank=False)
    
    # optional picture
    image = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        app_label= APPLICATION_LABEL