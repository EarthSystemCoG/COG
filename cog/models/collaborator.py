from django.db import models
from constants import APPLICATION_LABEL, RESEARCH_KEYWORDS_MAX_CHARS
from project import Project

class Collaborator(models.Model):
    
    first_name = models.CharField(max_length=100, blank=False, default='')
    last_name = models.CharField(max_length=100, blank=False, default='')
    institution = models.CharField(max_length=100, blank=False, default='')
    researchKeywords = models.CharField(max_length=RESEARCH_KEYWORDS_MAX_CHARS, blank=True, null=True, default='')
    project = models.ForeignKey(Project, blank=False)
    
    # optional picture
    image = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        app_label= APPLICATION_LABEL