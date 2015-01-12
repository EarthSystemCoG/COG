'''
Views for CoG Forum.

@author: cinquini
'''

from django.shortcuts import get_object_or_404, render_to_response

from cog.models.project import Project
from cog.models.forum import Forum, ForumThread
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from constants import PERMISSION_DENIED_MESSAGE

def forum_detail(request, project_short_name):
    '''View to display a forum index of threads.'''

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # get or create project forum
    (forum, created) = Forum.objects.get_or_create(project=project)
    
    # retrieve all threads for this project
    threads = ForumThread.objects.filter(forum=forum).order_by('-create_date')
    
    return render_to_response('cog/forum/forum_detail.html',
                              {'threads': threads,
                               'title': '%s Forum' % project.short_name,
                               'project': project },
                              context_instance=RequestContext(request))

def thread_detail(request, project_short_name, thread_id):
    '''View to display all comments associated with a given forum thread.'''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # retrieve requested thread
    thread = get_object_or_404(ForumThread, id=thread_id)
    
    return render_to_response('cog/forum/thread_detail.html',
                              {'thread': thread,
                               'title': '%s: %s' % (project.short_name, thread.title),
                               'project': project },
                              context_instance=RequestContext(request))
@login_required
def thread_update(request, project_short_name, thread_id):
    pass

@login_required
def thread_delete(request, project_short_name, thread_id):
    
    # retrieve requested thread
    thread = get_object_or_404(ForumThread, id=thread_id)
    
    # thread can be deleted only by original author, or site administrator
    if request.user != thread.author and not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # delete thread (and associated comments)
    thread.delete()
    
    # redirect to forum
    return HttpResponseRedirect( reverse('forum_detail', kwargs={'project_short_name':thread.getProject().short_name}) )
    
    

def forumthread_detail(request, forumthread_id):
    '''This view is needed to support a common implementation for log_comment_event.
       It redirects to the project-aware thread view.'''
    
    # retrieve requested thread
    thread = get_object_or_404(ForumThread, id=forumthread_id)
    
    url = reverse('thread_detail', kwargs={ 'thread_id':thread.id, 'project_short_name':thread.getProject().short_name })
    
    return HttpResponseRedirect( url )
