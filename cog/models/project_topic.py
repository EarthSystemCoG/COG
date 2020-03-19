from django.db import models
from .constants import APPLICATION_LABEL
from .topic import Topic
from .project import Project

# intermediate model for Project-Topic association
class ProjectTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # topic order within project index
    order = models.IntegerField(blank=False, null=False, default=0)
    
    class Meta:
        app_label= APPLICATION_LABEL