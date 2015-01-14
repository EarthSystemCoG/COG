'''
Views for CoG Forum.

@author: cinquini
'''

from django.shortcuts import get_object_or_404, render_to_response

from cog.models.project import Project, userHasAdminPermission, userHasUserPermission
from cog.models.forum import Forum, ForumThread, ForumTopic
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from constants import PERMISSION_DENIED_MESSAGE
from cog.forms.forms_forum import ForumThreadForm, MyCommentForm, ForumTopicForm
from django.utils.timezone import now
from django_comments.models import Comment

def forum_detail(request, project_short_name):
    '''View to display a list of all forum topics.
       This view is also used to shortcut the creation of a new forum topic.'''

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # get or create project forum
    (forum, created) = Forum.objects.get_or_create(project=project)
    
    # retrieve all topics for this project
    _topics = ForumTopic.objects.filter(forum=forum).order_by('title')
    
    # filter by privacy settings
    topics = [t for t in _topics if not t.is_private or userHasUserPermission(request.user, project) ]
    
    # GET request to list all threads
    if request.method=='GET':
        
        # create new empty form
        form = ForumTopicForm()
        
        # display forum index
        return _render_forum_template(topics, project, form, request)
                
    # POST request to create new thread
    else:
        
        # topics can only be created by project administrators
        if not userHasAdminPermission(request.user, project):
            return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            
            # create a new thread object but don't save it to the database yet
            topic = form.save(commit=False)
            # modify the topic object
            topic.author = request.user
            topic.forum = project.forum
            # save topic to database
            topic.save()
                        
            # FIXME: redirect to topic page instead ?
            return HttpResponseRedirect( reverse('forum_detail', 
                                                 kwargs={'project_short_name':project.short_name}) )

        else:
            
            # display forum index with errors
            return _render_forum_template(topics, project, form, request)

def topic_detail(request, project_short_name, topic_id):
    '''View to display a list of all threads for a given forum topic.
       This view is also used to shortcut the creation of a new thread.'''

    # retrieve objects from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    topic = get_object_or_404(ForumTopic, id=topic_id)
    threads = ForumThread.objects.filter(topic=topic).order_by('-create_date')
    
    # GET request to list all threads
    if request.method=='GET':
        
        # create new empty form
        form = ForumThreadForm(initial={'topic':topic})
        
        # display forum index
        return _render_topic_template(project, topic, threads, form, request)
                
    # POST request to create new thread
    else:
        
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            
            # create a new thread object but don't save it to the database yet
            thread = form.save(commit=False)
            # modify the thread object
            thread.author = request.user
            # save thread to database
            thread.save()
                        
            return HttpResponseRedirect( reverse('topic_detail', 
                                                 kwargs={'project_short_name':project.short_name, 'topic_id':topic.id}) )

        else:
            
            # display forum index with errors
            return _render_forum_template(threads, project, form, request)
        
@login_required
def topic_delete(request, project_short_name, topic_id):
    
    # retrieve database objects
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # topics can be deleted only by project administrators
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # delete thread (and associated comments)
    topic.delete()
    
    # redirect to forum
    return HttpResponseRedirect( reverse('forum_detail', kwargs={'project_short_name':project.short_name}) )

def _render_topic_template(project, topic, threads, form, request):
    
    return render_to_response('cog/forum/topic_detail.html',
                              {'title': '%s Forum: %s' % (project.short_name, topic.title),
                               'project': project,
                               'topic': topic,
                               'threads':threads,
                               'form':form },
                              context_instance=RequestContext(request))

    
            
def _render_forum_template(topics, project, form, request):
    
    return render_to_response('cog/forum/forum_detail.html',
                              {'topics': topics,
                               'title': '%s Forum' % project.short_name,
                               'project': project,
                               'form':form },
                              context_instance=RequestContext(request))
    
def thread_detail(request, project_short_name, thread_id):
    '''View to display all comments associated with a given forum thread.'''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # retrieve requested thread
    thread = get_object_or_404(ForumThread, id=thread_id)
                    
    return _render_thread_template(request, project, thread) 
            
    
def _render_thread_template(request, project, thread):
    
    return render_to_response('cog/forum/thread_detail.html',
                              {'thread': thread,
                               'title': '%s: %s' % (project.short_name, thread.title),
                               'project': project },
                              context_instance=RequestContext(request))
    
@login_required
def comment_update(request, comment_id):
    
    # retrieve requested comment
    comment = get_object_or_404(Comment, id=comment_id)
    
    # comments can be updated only by original author or project administrator
    project = comment.content_object.getProject()
    if not userHasAdminPermission(request.user, project) and comment.user!=request.user:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method=='GET':
        
        form = MyCommentForm(initial={ 'text':comment.comment } )
        
        return render_to_response('cog/forum/comment_form.html',
                                  { 'title': 'Update Comment',
                                    'project':project, 
                                    'comment':comment,
                                    'form':form },
                                  context_instance=RequestContext(request))
    else:
        
        form = MyCommentForm(request.POST)
        
        if form.is_valid():
            # update comment text from form
            text = form.cleaned_data['text']
            comment.comment = text
            comment.save()
            
            return HttpResponseRedirect( reverse('thread_detail', kwargs={ 'thread_id':comment.content_object.id, 
                                                                          'project_short_name':project.short_name }) )

            
        else:
            return render_to_response('cog/forum/comment_form.html',
                                  { 'title': 'Update Comment',
                                    'project':project, 
                                    'comment':comment,
                                    'form':form },
                                  context_instance=RequestContext(request))
 
@login_required
def topic_update(request, project_short_name, topic_id):
    
    # retrieve objects from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # topics can be updated only by project administrators
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    if request.method=='GET':
        
        form = ForumTopicForm(instance=topic)
        
        return _render_topic_form(request, project, topic, form)
        
    else:
    
        form = ForumTopicForm(request.POST, instance=topic)
        
        if form.is_valid():
            
            topic = form.save()
            return HttpResponseRedirect( reverse('topic_detail', kwargs={ 'topic_id':topic.id, 'project_short_name':project.short_name }) )
            
        else:
            return _render_topic_form(request, project, topic, form)

def _render_topic_form(request, project, topic, form):

    return render_to_response('cog/forum/topic_form.html',
                              {'topic': topic, 
                               'title': '%s: %s Update' % (project.short_name, topic.title),
                               'project':project, 
                               'form':form },
                              context_instance=RequestContext(request))


    
@login_required
def thread_update(request, project_short_name, thread_id):
    
    # retrieve requested thread
    thread = get_object_or_404(ForumThread, id=thread_id)
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # thread can be updated only by original author, or project administrator
    if not userHasAdminPermission(request.user, project) and thread.author!=request.user:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    if request.method=='GET':
        
        form = ForumThreadForm(instance=thread)
        
        return render_to_response('cog/forum/thread_form.html',
                                  {'thread': thread, 
                                   'title': 'Update Forum Thread %s: %s' % (project.short_name, thread.title),
                                   'project':project, 
                                   'form':form },
                                  context_instance=RequestContext(request))
        
    else:
    
        form = ForumThreadForm(request.POST, instance=thread)
        
        if form.is_valid():
            
            thread = form.save()
            
            return HttpResponseRedirect( reverse('thread_detail', kwargs={ 'thread_id':thread.id, 'project_short_name':project.short_name }) )
            
            
        else:
            return render_to_response('cog/forum/thread_form.html',
                          {'thread': thread, 
                           'title': 'Update Forum Thread %s: %s' % (project.short_name, thread.title),
                           'project':project, 
                           'form':form },
                          context_instance=RequestContext(request))


@login_required
def thread_delete(request, project_short_name, thread_id):
    
    # retrieve requested thread
    thread = get_object_or_404(ForumThread, id=thread_id)
    
    # thread can be deleted only by original author, or project administrator
    if not userHasAdminPermission(request.user, thread.getProject()) and thread.author!=request.user:
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
