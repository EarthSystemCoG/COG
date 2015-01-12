'''
CoG forum models.

@author: Luca Cinquini
'''

from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from django.contrib.auth.models import User
from topic import Topic
from django_comments.moderation import CommentModerator, moderator
from cog.notification import notify
from django.core.urlresolvers import reverse

class Forum(models.Model):
    '''Top-level forum specific to each project, contains one or more Discussion.'''

    project = models.OneToOneField(Project, blank=False, related_name='forum')
        
    def __unicode__(self):
        return "%s Forum" % self.project.short_name
        
    class Meta:
        app_label= APPLICATION_LABEL
        
class ForumThread(models.Model):
    '''Group of forum posting about a specified topic.'''
    
    forum = models.ForeignKey(Forum, blank=False, related_name='threads')
    author = models.ForeignKey(User, related_name='threads', verbose_name='Author', blank=False, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, verbose_name='Title', blank=False)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    update_date = models.DateTimeField('Date Updated', auto_now=True)
    # order of discussion within forum (for later reordering)
    order = models.IntegerField(blank=True, null=False, default=0)
    # optional topic
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.SET_NULL)
    # optional attached documents - must specify both blank=True (form validation) and null=True (model)
    #docs = models.ManyToManyField(Doc, verbose_name='Attachments', blank=True, null=True)    
    # public/private flag: discussion can only be viewed by project members
    is_private = models.BooleanField(verbose_name='Private?', default=False, null=False)
    # restricted flag: restricted posts can only be edited by project administrators
    #is_restricted = models.BooleanField(verbose_name='Restricted?', default=False, null=False)
    
    def getProject(self):
        return self.forum.project
    
    def __unicode__(self):
        return self.title

    class Meta:
        app_label= APPLICATION_LABEL    
        
class ForumModerator(CommentModerator):
    '''Custom comment moderator class that sends email to project administrators.'''
    
    email_notification = True
    
    def email(self, comment, content_object, request):
        
        thread = comment.content_object
        project = thread.getProject()
        
        # check project forum notification flag
        if project.forumNotificationEnabled:
        
            # build emai 
            user = comment.user
            
            subject = "[%s] Forum posting" % project.short_name
            # thread url: http://localhost:8000/projects/TestProject/thread/2/
            url = reverse('thread_detail', kwargs={ 'project_short_name':project.short_name.lower(), 'thread_id':thread.id })
            url = request.build_absolute_uri(url)        
            # specific comment url: http://localhost:8000/projects/TestProject/thread/2/?c=17
            message = "User: %s\n Thread: %s\n Comment: %s\n" % (user, url, comment.comment)
    
            # send email                
            for admin in project.getAdminGroup().user_set.all():
                notify(admin, subject, message)

moderator.register(ForumThread, ForumModerator)    
