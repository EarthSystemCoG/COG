from cog.forms import *
from cog.models import *
from cog.utils import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from string import Template
from urllib import quote, unquote
import copy
from constants import PERMISSION_DENIED_MESSAGE
from views_project import getProjectNotActiveRedirect, getProjectNotVisibleRedirect

# view to render a generic post
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Check page access
    redirect = getNotAuthorizedRedirect(request, post)
    if redirect is not None:
        return redirect
            
    # if page, redirect to page view
    if post.type==Post.TYPE_PAGE:
        return HttpResponseRedirect( post.url )
    
    # if blog or notes, render template
    else:              
        return render_to_response('cog/post/post_detail.html', 
                                  {'post':post, 'project':post.project, 'title':post.title }, context_instance=RequestContext(request))
    
# view to delete a post (page or blog)
def post_delete(request, post_id):
    
    # retrieve post
    post = get_object_or_404(Post, pk=post_id)
    project = post.project
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
    # check post is not one of the critical project pages
    if post.is_predefined():
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method=='GET':
        return render_to_response('cog/post/post_delete.html', 
                                  {'post':post, 'project':project, 'title':'%s Deletion Request' % post.type.capitalize() }, 
                                  context_instance=RequestContext(request))
    else:
             
        # pass a temporary copy of the object to the view
        _post = copy.copy(post)  
        
        # delete the post
        post.delete()
    
        return render_to_response('cog/post/post_delete.html', 
                                  {'post':_post, 'project':project, 'title':'%s Deletion Confirmation' % _post.type.capitalize() }, 
                                  context_instance=RequestContext(request))


# view to render a page post
def page_detail(request, project_short_name):
             
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check project is active
    if project.active==False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)
        
    # load page with URL equal to request path
    url = quote(request.path)

    #page = get_object_or_404(Post, url=quote(request.path))
    try:
        page = Post.objects.get(url=url)
    except Post.DoesNotExist:
        print 'Page does not exist, creating it'
        # dynamically create page if url matches one of the pre-defined values
        page = create_project_page(url, project)
        # if page has not been created, return error
        if not page:
            raise Http404
    
    # Check page access
    redirect = getNotAuthorizedRedirect(request, page)
    if redirect is not None:
        return redirect
    
    dict = {"title": page.title, "post": page, "project" : project }
    
    # add extra objects for home page
    # FIXME
    if page.is_home:
            dict['project_latest_news']=project.news()[0:5]
            dict['project_latest_signals']=project.signals()[0:5]
            
    # render page template
    return render_to_response(page.template, dict, context_instance=RequestContext(request) )

# view to render project home, delegates to the home page URL
def project_home(request, project_short_name):
    
    return page_detail(request, project_short_name.lower())
    #project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
# Note: method=GET always
def post_list(request, project_short_name):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    # query by project
    qset = Q(project=project)
           
    # query by type
    type = request.GET.get('type', None)
    qset = qset & Q(type=type)
    list_title = 'All %ss' % type.capitalize()
    
    # text query
    query = request.GET.get('query', '')
    if query:
        qset = qset & ( Q(title__icontains=query) | Q(body__icontains=query) | Q(author__first_name__icontains=query) | Q(author__last_name__icontains=query) | Q(author__username__icontains=query) )
        list_title = "Search Results for '%s'" % query
    
    # topic constraint
    topic = request.GET.get('topic', '')
    if topic:
        qset = qset & Q(topic__name=topic)
        list_title += ' [topic=%s]' % topic
        
    # execute query, order by descending update date or title
    sortby = request.GET.get('sortby', 'title')
    if sortby=='date':
        results = Post.objects.filter(qset).distinct().order_by('-update_date')
    else:
        results = Post.objects.filter(qset).distinct().order_by('title')
                
    # list all possible topics for posts of this project, and of given type
    # must follow the foreign key relation Post -> Topic backward (through 'topic.post_set')
    #topic_list = Topic.objects.all().order_by('name')
    topic_list = Topic.objects.filter( Q(post__project=project) & Q(post__type=type) ).distinct().order_by('-name')

    return render_to_response('cog/post/post_list.html', 
                              {"object_list": results, 
                               "title": "%s %ss" % (project.short_name, type.capitalize()),
                               "list_title":list_title,
                               "query": query,  
                               "project" : project,
                               "topic":topic, "topic_list":topic_list}, 
                               context_instance=RequestContext(request))
            
@login_required
def post_add(request, project_short_name, owner=None):
    '''
    View to create a Post object within a context project.
    Optionally, an owner object can be specified, which is assigned a reference to the newly created Post
    through its method .setPost(Post)
    '''
    
    # load project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasUserPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    # retrieve type
    type = request.REQUEST.get('type')
  
    if request.method=='GET':
        
        # create empty Post object, pre-populate project and type
        post = Post()
        post.project = project
        post.type = type
        
        # optionally assign parent Post
        parent_id = request.GET.get('parent_id', None)
        if (parent_id):
            ppost = get_object_or_404(Post, pk=parent_id)
            post.parent = ppost
            post.topic = ppost.topic
             
        # create form from instance
        # note extra argument project to customize the queryset!
        form = PostForm(type, project, instance=post)
        return render_post_form(request, form, project, type)
    
    else:
        # create form object from form data
        form = PostForm(type, project, request.POST)
        if form.is_valid():
            # create a new post object but don't save it to the database yet
            post = form.save(commit=False)
            # modify the post object
            post.author = request.user
            # page: build full page URL
            if post.type==Post.TYPE_PAGE:
                post.url = get_project_page_full_url(project, post.url)
            else:
                # assign temporary value before object id is assigned
                post.url = datetime.now()
            # assign post order, if top-level
            # note that the post.topic may be None
            if post.parent is None:
                pages = Post.objects.filter(project=project).filter(topic=post.topic).order_by('order')
                post.order = len(pages)+1
            else:
                post.order = 0
            # save post object to the database (GET-POST-REDIRECT)
            post.save()
            # assign post URL and save again
            if post.type==Post.TYPE_BLOG or post.type==Post.TYPE_NOTES:
                post.url = reverse('post_detail', args=[post.id])
                post.save()
                
            # create project-topic relation if not existing already
            if post.topic is not None:
                createProjectTopicIfNotExisting(project, post.topic)
                    
            # assign this reference to owner
            if owner is not None:
                owner.setPost(post)
                owner.save()
                
            # redirect to post (GET-POST-REDIRECT)
            return redirect_to_post(request, post)
                
        # invalid data
        else:
            print form.errors
            return render_post_form(request, form, project, type)
        
def createProjectTopicIfNotExisting(project, topic):
    try:
        pt = ProjectTopic.objects.get(project=project,topic=topic)
    except ProjectTopic.DoesNotExist:
        pt = ProjectTopic(project=project,topic=topic, order=len(project.topics.all())+1)
        pt.save()

# function to return an error message if a post object is locked
def getPostIsLockedRedirect(request, project, post, lock):
        messages = ["The page '%s' is currently edited by %s" % (post.title, lock.owner.get_full_name()),
                    "The current lock will expire at %s" % lock.get_expiration().strftime('%Y-%m-%d %H:%M:%S') ] 
        return render_to_response('cog/common/message.html', 
                                  {'mytitle':'Page is locked', 
                                   'project':project,
                                   'messages':messages }, 
                                  context_instance=RequestContext(request))
        
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
    return HttpResponseRedirect( reverse('post_detail', kwargs={'post_id': post.id}))
    
        
@login_required
def post_update(request, post_id):
        
    # retrieve post object from database
    post = get_object_or_404(Post, pk=post_id)
        
    # check permission
    if not userCanPost(request.user, post):
        raise PermissionDenied
    
    # check lock
    lock = getLock(post)
    if isLockedOut(request.user, lock):
        return getPostIsLockedRedirect(request, post.project, post, lock)
    # create/renew lock
    lock = createLock(post, request.user)
    
    if (request.method=='GET'):
                
        # extract page partial URL
        if post.type==Post.TYPE_PAGE:
            post.url = get_project_page_sub_url(post.project, post.url)
        
        # create form object from model
        form = PostForm(post.type, post.project, instance=post)
                
        return render_post_form(request, form, post.project, post.type, lock=lock)
        
    else:
        # update existing database model with form data
        form = PostForm(post.type, post.project, request.POST, instance=post)
        #print "1 PAGE URL=%s" % form.data['url']
        if (form.is_valid()):
            # build instance from form data
            post = form.save(commit=False)
            # rebuild full page URL
            if post.type==Post.TYPE_PAGE:
                post.url = get_project_page_full_url(post.project, post.url)
            # change the author to the last editor
            post.author = request.user
            # save instance
            post.save()
            # create project-topic relation if not existing already
            if post.topic is not None:
                createProjectTopicIfNotExisting(post.project, post.topic)
                
            # release lock
            deleteLock(post)

            # redirect to post (GET-POST-REDIRECT)
            return redirect_to_post(request, post)
        else:
            print form.errors
            return render_post_form(request, form, post.project, post.type, lock=lock)
        
@login_required
def post_add_doc(request, post_id):

    # retrieve post from database
    post = get_object_or_404(Post, pk=post_id)
    
     # retrieve doc from database
    doc_id = request.GET.get('doc_id',None)
    doc = get_object_or_404(Doc, pk=doc_id)
    
    # check permission
    if not userCanPost(request.user, post):
        raise PermissionDenied
    
    # attach doc to post
    post.docs.add(doc)
    post.save()
    
    return HttpResponseRedirect( reverse('post_detail', kwargs={'post_id': post.id}) )
    
@login_required
def post_remove_doc(request, post_id, doc_id):

    # retrieve post from database
    post = get_object_or_404(Post, pk=post_id)
    
    # check permission
    if not userCanPost(request.user, post):
        raise PermissionDenied
    
    # retrieve doc from database
    doc = get_object_or_404(Doc, pk=doc_id)
    
    # check doc is attached to post
    if post.docs.get(id=doc_id):
        # remove doc from post
        post.docs.remove(doc)
        post.save()
        # delete doc
        doc.delete()
    
    return HttpResponseRedirect( reverse('post_detail', kwargs={'post_id': post.id}) )
        
def render_post_form(request, form, project, type, lock=None):
    
    #type = request.GET.get('type', None)
    title = "%s Editor" % type.capitalize() 
    return render_to_response('cog/post/post_form.html', 
                             {'form': form, 'project':project, 'title':title, 'lock':lock}, 
                              context_instance=RequestContext(request))

# function to redirect to the post blog/page URL
def redirect_to_post(request, post):
    if post.type=='blog':
        return HttpResponseRedirect( reverse('post_detail', kwargs={'post_id':post.id}) )
    else:
        return HttpResponseRedirect(post.url)
    
# function to check that the user can modify the given post
def userCanPost(user, post):
    # project members can modify any page except for the home page
    #if post.is_home:     
    #    if not userHasAdminPermission(user, post.project):
    #        return False
    #else:
    #    if not userHasUserPermission(user, post.project):
    #        return False
    #return True
    # all project members can modify all pages
    return userHasUserPermission(user, post.project)

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
    if post.project.active==False:
        return getProjectNotActiveRedirect(request, post.project)
    elif post.project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, post.project)
    
    # use is NOT authorized
    if not userCanView(request.user, post):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login')+"?next=%s" % request.path)
        else:
             messages = ['This page is restricted to member of project %s' % post.project.short_name,
                         'Please contact support for any questions.'] 
             return render_to_response('cog/common/message.html', 
                              {'mytitle':'Page Access Restricted', 
                               'project':post.project,
                               'messages':messages }, 
                              context_instance=RequestContext(request))    

    # use is authorized, return no redirect
    else:
        return None