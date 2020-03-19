from django.db import models
from .constants import APPLICATION_LABEL, SIGNAL_OBJECT_CREATED, SIGNAL_OBJECT_UPDATED, SIGNAL_OBJECT_DELETED
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.signals import request_finished
from django.urls import reverse
from django.dispatch import receiver
from .post import Post, post_signal
from .doc import Doc
from .news import News


class LoggedEvent(models.Model):
    '''Class that represents an important event that is logged to the database.'''

    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    description = models.CharField(max_length=200, blank=False)
    url = models.URLField(blank=True)
    update_date = models.DateTimeField('Date Time', auto_now_add=True)
    sender = models.CharField(max_length=200, blank=True)

    class Meta:
        app_label = APPLICATION_LABEL


# receiver function for instance creation/update events
def log_instance_event(sender, **kwargs):
    instance = kwargs['instance']
    user = instance.author
    project = instance.project
    classname = instance.__class__.__name__
    if kwargs['created']:
        title = 'New %s created' % get_display_name(instance, classname)
    else:
        title = '%s updated' % get_display_name(instance, classname)
    if user is not None:
        event = LoggedEvent.objects.create(user=user, project=project, title=title, description=instance.title,
                                           sender='%s' % sender,
                                           url=reverse('%s_detail' % classname.lower(),
                                                       kwargs={'%s_id' % classname.lower(): instance.id}))
        event.save()




def get_display_name(instance, classname):
    if classname == 'Doc':
        return 'Document'
    elif classname == 'Post':
        return instance.type.capitalize()
    else:
        return classname


# These are all the receivers for the various signals. We could do this with a @receiver before each function as well
# Note: must use a unique string for "dispatch_id" to prevent functions from being called again every time the
# module is imported
# post_save.connect(log_instance_event, sender=Post, dispatch_uid="log_post_event")
post_save.connect(log_instance_event, sender=Doc, dispatch_uid="log_doc_event")
post_save.connect(log_instance_event, sender=News, dispatch_uid="log_news_event")

# callback receiver function for Post update events
@receiver(post_signal)
def post_signal_receiver(sender, **kwargs):

    instance = sender
    signal_type = kwargs['signal_type']

    project = instance.project
    user = instance.author
    classname = instance.__class__.__name__
    if signal_type == SIGNAL_OBJECT_CREATED:
        title = 'New %s created' % get_display_name(instance, classname)
    elif signal_type == SIGNAL_OBJECT_UPDATED:
        title = '%s updated' % get_display_name(instance, classname)
    elif signal_type == SIGNAL_OBJECT_DELETED:
        title = '%s deleted' % get_display_name(instance, classname)
    else:
        title = 'Unknown action for %s' % get_display_name(instance, classname)

    if user is not None:
        event = LoggedEvent.objects.create(user=user, project=project, title=title, description=instance.title,
                                           sender='%s' % sender,
                                           url=reverse('%s_detail' % classname.lower(),
                                                       kwargs={'%s_id' % classname.lower(): instance.id}))
        event.save()
