from cog.forms import *
from cog.models import *
from cog.models.auth import userHasContributorPermission, userHasAdminPermission, userHasUserPermission
from cog.utils import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from string import Template
from urllib import quote, unquote
import copy
from constants import PERMISSION_DENIED_MESSAGE, LOCAL_PROJECTS_ONLY_MESSAGE
from cog.models.constants import SIGNAL_OBJECT_CREATED, SIGNAL_OBJECT_UPDATED, SIGNAL_OBJECT_DELETED
from utils import getProjectNotActiveRedirect, getProjectNotVisibleRedirect
from django.utils.timezone import now
from cog.models.utils import delete_doc
from django.conf import settings
import os
from cog.views.utils import getQueryDict, paginate


# view to render a generic post
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Check page access
    redirect = getNotAuthorizedRedirect(request, post)
    if redirect is not None:
        return redirect
            
    # if page, redirect to page view
    if post.type == Post.TYPE_PAGE:
        return HttpResponseRedirect(post.url)
    
    # if blog or notes, render template
    else:
        return render(request,
                      'cog/post/post_detail.html',
                      {'post': post, 'project': post.project, 'title': post.title})


# view to delete a post (page or blog)
def post_delete(request, post_id):
    
    # retrieve post
    post = get_object_or_404(Post, pk=post_id)
    project = post.project
            
    # check post is not one of the critical project pages
    if post.is_predefined():
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    else:
        # check permission: only project members can delete non-predefined project pages
        if not userHasContributorPermission(request.user, project):
            return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method == 'GET':
        return render(request,
                      'cog/post/post_delete.html', 
                      {'post': post, 'project': project,
                       'title': '%s Deletion Request' % post.type.capitalize()})
    else:
             
        # pass a temporary copy of the object to the view
        _post = copy.copy(post)  
                
        # send post update signal
        post.send_signal(SIGNAL_OBJECT_DELETED)
                
        # delete the post
        post.delete()
    
        return render(request,
                      'cog/post/post_delete.html', 
                      {'post': _post, 'project': project,
                       'title': '%s Deletion Confirmation' % _post.type.capitalize()})


# view to render a page post
def page_detail(request, project_short_name):
             
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
        
    # HTTP redirect for non-local projects
    if not project.isLocal():
        return HttpResponseRedirect("http://%s%s" % (project.site.domain, request.path))
    
    # check project is active
    if project.active == False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)
        
    # load page with URL equal to request path
    url = quote(request.path)

    #page = get_object_or_404(Post, url=quote(request.path))
    #TODO: add another case...if project description or long_name has changed.
    try:
        page = Post.objects.get(url=url)
    except Post.DoesNotExist:
        # dynamically create a templated project page if url matches one of the pre-defined values
        page = create_project_page(url, project)
        # if page has not been created, return error
        if not page:
            raise Http404
    
    # Check page access
    redirect = getNotAuthorizedRedirect(request, page)
    if redirect is not None:
        return redirect

    dict = {"title": page.title, "post": page, "project": project}
    
    related_pages = []
    for post in page.post_set.all():
        if not post.is_predefined():
            related_pages.append(post)
    dict['related_pages'] = related_pages
    
    # add extra objects for home page
    if page.is_home:
        dict['project_latest_signals'] = project.signals()[0:5]
            
    # render page template
    return render(request, page.template, dict)


# view to render project home, delegates to the home page URL
def project_home(request, project_short_name):
    
    if project_short_name == project_short_name.lower():
        return page_detail(request, project_short_name)
    # redirect mixed-case requests to use lower case project name
    else:
        return HttpResponseRedirect(reverse('project_home', args=[project_short_name.lower()]))
    
    
# Note: method=GET always
def post_list(request, project_short_name):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # query by project
    qset = Q(project=project)

    #TODO: remove type query if not needed (type is all posts)
    # query by type
    #type = request.GET.get('type', None)
    type = 'post'
    qset = qset & Q(type=type)
    list_title = 'List All Pages'

    #TODO: remove text query if not needed
    # text query
    query = request.GET.get('query', '')
    #if query:
    #    qset = qset & (Q(title__icontains=query) | Q(body__icontains=query) | Q(author__first_name__icontains=query) |
    #                   Q(author__last_name__icontains=query) | Q(author__username__icontains=query))
     #   list_title = "Search Results for '%s'" % query
    
    # topic constraint
    topic = request.GET.get('topic', '')
    #if topic:
    #    qset = qset & Q(topic__name=topic)
    #    list_title += ' [topic=%s]' % topic
        
    # execute query, order by descending update date or title
    sortby = request.GET.get('sortby', 'title')
    if sortby == 'date':
        results = Post.objects.filter(project=project).distinct().order_by('-update_date')
    elif sortby == 'topic':
        results = Post.objects.filter(project=project).distinct().order_by('-topic')
    else:
        results = Post.objects.filter(project=project).distinct().order_by('title')
                
    # list all possible topics for posts of this project, and of given type
    # must follow the foreign key relation Post -> Topic backward (through 'topic.post_set')

	#TODO: remove topic list if not used
    #topic_list = Topic.objects.all().order_by('name')
    topic_list = Topic.objects.filter(Q(post__project=project) & Q(post__type=type)).distinct().order_by('-name')

    return render(request,
                  'cog/post/post_list.html', 
                  {"object_list": paginate(results, request, max_counts_per_page=50),
                   "title": '%s Pages' % project.short_name,
                   "list_title": list_title,
                   "query": query,  
                   "project": project,
                   "topic": topic,
                   "topic_list": topic_list})


@login_required
def post_add(request, project_short_name, owner=None):
    """
    View to create a Post object within a context project.
    Optionally, an owner object can be specified, which is assigned a reference to the newly created Post
    through its method .setPost(Post)
    """
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasContributorPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    # retrieve type
    postType = getQueryDict(request).get('type')
  
    if request.method == 'GET':
        
        # create empty Post object, pre-populate project and type
        post = Post()
        post.project = project
        post.type = postType
        
        # optionally assign parent Post
        parent_id = request.GET.get('parent_id', None)
        if parent_id:
            ppost = get_object_or_404(Post, pk=parent_id)
            post.parent = ppost
            post.topic = ppost.topic
            
        # set fixed fields for hyperlinks
        #if postType == Post.TYPE_HYPERLINK:
        #    post.template = None
        #    post.is_private = False
        #    post.is_restricted = False
             
        # create form from instance
        # note extra argument project to customize the queryset!
        form = PostForm(postType, project, instance=post)
        return render_post_form(request, form, project, postType)
    
    else:
        # create form object from form data
        form = PostForm(postType, project, request.POST)
        if form.is_valid():
            # create a new post object but don't save it to the database yet
            post = form.save(commit=False)
            # modify the post object
            post.author = request.user
            # update date 
            post.update_date = now()

            # page: build full page URL
            if post.type == Post.TYPE_PAGE:
                post.url = get_project_page_full_url(project, post.url)
            elif post.type != Post.TYPE_HYPERLINK:
                # assign temporary value before object id is assigned
                post.url = datetime.now()
            # assign post order, if top-level
            # note that the post.topic may be None
            if post.parent is None:
                pages = Post.objects.filter(project=project).filter(topic=post.topic).filter(parent=None).\
                    filter(Q(type=Post.TYPE_PAGE) | Q(type=Post.TYPE_HYPERLINK)).order_by('order')
                post.order = len(pages)+1
            else:
                post.order = 0
            # save post object to the database (GET-POST-REDIRECT)
            post.save()
            # assign post URL and save again
            if post.type == Post.TYPE_BLOG or post.type == Post.TYPE_NOTES:
                post.url = reverse('post_detail', args=[post.id])
                post.save()
                
            # create project-topic relation if not existing already
            if post.topic is not None:
                createProjectTopicIfNotExisting(project, post.topic)
                    
            # assign this reference to owner
            if owner is not None:
                owner.setPost(post)
                owner.save()
                       
            # send post update signal
            post.send_signal(SIGNAL_OBJECT_CREATED)
                
            # redirect to post (GET-POST-REDIRECT)
            if post.type != Post.TYPE_HYPERLINK:
                return redirect_to_post(request, post)
            # or to project home page
            else:
                return HttpResponseRedirect(reverse('project_home', args=[project_short_name.lower()]))
                
        # invalid data
        else:
            return render_post_form(request, form, project, postType)


def createProjectTopicIfNotExisting(project, topic):
    try:
        pt = ProjectTopic.objects.get(project=project, topic=topic)
    except ProjectTopic.DoesNotExist:
        pt = ProjectTopic(project=project, topic=topic, order=len(project.topics.all())+1)
        pt.save()


# function to return an error message if a post object is locked
def getLostLockRedirect(request, project, post, lock):
        messages = ["Sorry, your lock on this page has expired, and others have modified the page afterwards.",
                    "Your changes cannot be saved. Please start the update from most current version of the page."]
        return render(request,
                      'cog/common/message.html', 
                      {'mytitle': 'Changes cannot be saved',
                       'project': project,
                       'messages': messages})


# function to return an error message if a user lost the lock on the object
def getPostIsLockedRedirect(request, project, post, lock):
        messages = ["The page '%s' is currently being edited by %s." % (post.title, lock.owner.get_full_name()),
                    "The current lock will expire at %s." % lock.get_expiration().strftime('%Y-%m-%d %H:%M:%S')]
        return render(request,
                      'cog/common/message.html', 
                      {'mytitle': 'Page is locked',
                       'project': project,
                       'messages': messages})


@login_required
def post_cancel(request, post_id):
    """View that releases the lock on a post when user clicks on 'Cancel', then redirects to the post."""
    
    # retrieve post object from database
    post = get_object_or_404(Post, pk=post_id)
    
    # check lock
    lock = getLock(post)
    if isLockedOut(request.user, lock):
        return getPostIsLockedRedirect(request, post.project, post, lock)
    
    # delete lock
    deleteLock(post)
    
    # redirect to post
    return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))
    
        
@login_required
def post_update(request, post_id):
        
    # retrieve post object from database
    post = get_object_or_404(Post, pk=post_id)
        
    # check permission
    if not userCanPost(request.user, post):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # check lock
    lock = getLock(post)
    if isLockedOut(request.user, lock):
        return getPostIsLockedRedirect(request, post.project, post, lock)
        
    if request.method == 'GET':
        
        # create/renew lock
        lock = createLock(post, request.user)
                
        # extract page partial URL
        if post.type == Post.TYPE_PAGE:
            post.url = get_project_page_sub_url(post.project, post.url)
        
        # create form object from model
        form = PostForm(post.type, post.project, instance=post)
                
        return render_post_form(request, form, post.project, post.type, lock=lock)
        
    else:
        
        # update existing database model with form data
        form = PostForm(post.type, post.project, request.POST, instance=post)

        # check versions       
        queryDict = getQueryDict(request)
        if post.version != int(queryDict.get('version', -1)):
            #print 'database version=%s form version=%s' % (post.version, queryDict.get('version', -1))
            return getLostLockRedirect(request, post.project, post, lock)

        #print "1 PAGE URL=%s" % form.data['url']
        if form.is_valid():
            # TODO: if hit cancel, form does not render, what is missing from save?

            # build instance from form data
            post = form.save(commit=False)
            form_data = form.clean()

            if form_data.get("save_only"):

                # save instance
                post.save()
                return render_post_form(request, form, post.project, post.type, lock=lock)
            else:
                # increment version
                post.version += 1
            
                # rebuild full page URL
                if post.type == Post.TYPE_PAGE:
                    post.url = get_project_page_full_url(post.project, post.url)

                # change the author to the last editor
                post.author = request.user

                # update date
                post.update_date = now()

                # save instance
                post.save()

                # create project-topic relation if not existing already
                if post.topic is not None:
                    createProjectTopicIfNotExisting(post.project, post.topic)

                # release lock
                deleteLock(post)

                # send post update signal
                post.send_signal(SIGNAL_OBJECT_UPDATED)

                # redirect to post (GET-POST-REDIRECT)
                if post.type != Post.TYPE_HYPERLINK:
                    return redirect_to_post(request, post)
                # or to project home page
                else:
                    return HttpResponseRedirect(reverse('project_home', args=[post.project.short_name.lower()]))

        else:
            return render_post_form(request, form, post.project, post.type, lock=lock)


@login_required
def post_add_doc(request, post_id):

    # retrieve post from database
    post = get_object_or_404(Post, pk=post_id)
    
     # retrieve doc from database
    doc_id = request.GET.get('doc_id', None)
    doc = get_object_or_404(Doc, pk=doc_id)
    
    # check permission
    if not userCanPost(request.user, post):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # attach doc to post
    post.docs.add(doc)
    
    # set the latest author of the page
    post.author = request.user    

    post.save()
    
    return HttpResponseRedirect( reverse('post_detail', kwargs={'post_id': post.id}))


@login_required
def post_remove_doc(request, post_id, doc_id):

    # retrieve post from database
    post = get_object_or_404(Post, pk=post_id)
    
    # check permission
    if not userCanPost(request.user, post):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # retrieve doc from database
    doc = get_object_or_404(Doc, pk=doc_id)
    
    # check doc is attached to post
    if post.docs.get(id=doc_id):
        delete_doc(doc)
    
    return HttpResponseRedirect( reverse('post_detail', kwargs={'post_id': post.id}))


def render_post_form(request, form, project, type, lock=None):
    
    #type = request.GET.get('type', None)
    title = "%s Editor" % type.capitalize() 
    return render(request,
                  'cog/post/post_form.html', 
                  {'form': form, 'project': project, 'title': title, 'lock': lock})


# function to redirect to the post blog/page URL
def redirect_to_post(request, post):
    if post.type == 'blog':
        return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))
    else:
        return HttpResponseRedirect(post.url)


# function to check that the user can modify the given post
def userCanPost(user, post):
    
    # page editing is restricted to project administrators
    if post.is_restricted:
        return userHasAdminPermission(user, post.project)
    # page can be edited by all project members
    else:
        return userHasContributorPermission(user, post.project)


# function to check whether the user can view the current page
def userCanView(user, post):
        
    # private pages can be viewed only by group members
    if post.is_private:
        return userHasUserPermission(user, post.project)
    # public pages are viewable by everybody
    else:
        return True


# function to check that the current user is authorized to view the requested page,
# and redirect the request appropriately if he/she isn't.
def getNotAuthorizedRedirect(request, post):
    
    # check project access first
    if post.project.active == False:
        return getProjectNotActiveRedirect(request, post.project)
    elif post.project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, post.project)
    
    # user is NOT authorized
    if not userCanView(request.user, post):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login')+"?next=%s" % request.path)
        else:
            messages = ['This page is only viewable to members of %s.' % post.project.short_name,
                        '<a href="/membership/request/%s">Request to join this project</a>.' % post.project.short_name]
            return render(request,
                          'cog/common/message.html', 
                          {'mytitle': 'Page Access Restricted',
                           'project': post.project,
                           'messages': messages})

    # user is authorized, return no redirect
    else:
        return None