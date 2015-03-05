import os
import string

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory, inlineformset_factory
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from cog.forms import *
from cog.models import *
from cog.models.navbar import TABS, TAB_LABELS, NAVMAP, INVNAVMAP
from cog.models.utils import *
from cog.models.utils import createOrUpdateProjectSubFolders
from cog.notification import notify
from cog.project_manager import projectManager
from cog.services.membership import addMembership
from cog.utils import *
from cog.views.constants import PERMISSION_DENIED_MESSAGE, LOCAL_PROJECTS_ONLY_MESSAGE
from cog.views.views_templated import templated_page_display
from cog.views.utils import add_get_parameter


# method to add a new project, with optional parent project
@login_required
def project_add(request):
    
    if request.method == 'GET':
        
        # associate project to current site
        current_site = Site.objects.get_current()
        project = Project(active=False, author=request.user, site=current_site)
        
        # optional parent project
        parent_short_name = request.GET.get('parent', None)
        if parent_short_name:
            parent = get_object_or_404(Project, short_name__iexact=parent_short_name)
            # check permission: only administrators of parent project can create parent child
            if not userHasAdminPermission(request.user, parent):
                return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
            project.parent = parent
        else:
            # check permission: only site administrators can create top-level projects
            #if not request.user.is_staff:
            #    return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
            parent = None
            
        # create list of unsaved project tabs
        tabs = get_or_create_project_tabs(project, save=False)
        
        # create list of unsaved project folders
        folders = getUnsavedProjectSubFolders(project, request)
        
        form = ProjectForm(instance=project)
        return render_to_response('cog/project/project_form.html',
                                  {'form': form, 'title': 'Register New Project', 'project': parent,
                                   'action': 'add', 'tabs': tabs, 'folders': folders},
                                  context_instance=RequestContext(request))
        
    else:
        
        # create form object from form data
        form = ProjectForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            # save object to the database - including the m2m relations to peer projects
            project = form.save()
            
            # create project tabs
            tabs = get_or_create_project_tabs(project, save=False)
            # set active state of project tabs from HTTP parameters 
            for tablist in tabs:
                setActiveProjectTabs(tablist, request, save=True)
                
            # create folders with appropriate state
            createOrUpdateProjectSubFolders(project, request)
            
            # notify site administrator
            notifySiteAdminsOfProjectRequest(project, request)
            
            # display confirmation message
            mytitle = 'New Project Confirmation'
            messages = ['Thank you for registering project: %s' % project.short_name,
                        'Your request will be reviewed by the site administrators as soon as possible,',
                        'and you will be notified of the outcome by email.']
            return render_to_response('cog/common/message.html',
                                      {'mytitle': 'New Project Confirmation', 'messages':messages},
                                      context_instance=RequestContext(request))
                    
        # invalid data
        else:
            
            print "Form is invalid: %s" % form.errors           
            project = form.instance
            
            # create and set state of project tabs, do not persist
            tabs = get_or_create_project_tabs(project=project, save=False)
            for tablist in tabs:
                setActiveProjectTabs(tablist, request, save=False)
                
            # rebuild list of unsaved project folders
            folders = getUnsavedProjectSubFolders(project, request)

            return render_to_response('cog/project/project_form.html', 
                                      {'form': form, 'title': 'Register New Project', 'action': 'add', 'tabs': tabs,
                                       'folders': folders},
                                      context_instance=RequestContext(request))
            
# method to reorganize the project index menu


@login_required
def project_index(request, project_short_name):
    
    TOPIC_ID = "topic_id_"
    PAGE_ID = "_page_id_"
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # limit to local projects only
    if not project.isLocal():
        return HttpResponseForbidden(LOCAL_PROJECTS_ONLY_MESSAGE)
        
    # check permission
    if not userHasAdminPermission(request.user, project) and not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    errors = {}
    index = site_index(project)
    
    # GET
    if request.method == 'GET':
        
        return render_to_response('cog/project/index_form.html', 
                                  {'index': index, 'title': 'Update Site Index', 'project': project, 'errors': errors},
                                  context_instance=RequestContext(request))
    # POST
    else:
        
        # retrieve current index, update according to form data
        index = site_index(project)
        # map (topic, new_order)
        topicMap = {} 
        valid = True  # form data validation flag
        
        for ii in index:
            topic = ii.topic
            pages = ii.pages
            
            # topic: skip first index_item
            if topic is None:
                topickey = TOPIC_ID
            else:
                topickey = TOPIC_ID + str(topic.id)
                topicvalue = request.POST[topickey]
                ii.order = topicvalue
                # validate topic order
                if topicvalue in topicMap.values():
                    valid = False
                    errors[topickey] = "Duplicate topic number: %d" % int(topicvalue)
                else:
                    topicMap[topickey] = topicvalue
                    
            # pages: process all
            pageMap = {}
            for page in pages:
                pagekey = topickey + PAGE_ID + str(page.id)
                pagevalue = request.POST[pagekey]
                page.order = pagevalue
                # validate page order
                if pagevalue in pageMap.values():
                    valid = False
                    errors[pagekey] = "Duplicate page number: %d" % int(pagevalue)
                else:
                    pageMap[page.id] = pagevalue
             
        # form data is valid              
        if valid:
            
            # save new ordering
            for ii in index:
                
                # skip None topic
                if ii.topic is not None:
                    projectTopic = ProjectTopic.objects.get(project=project, topic=ii.topic)
                    projectTopic.order = ii.order
                    projectTopic.save()
                
                # process all topic pages
                for page in ii.pages:
                    page.save()    
                            
            # redirect to project home (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('project_home', args=[project.short_name.lower()]))

        else:
            # return to form to fix validation errors
            return render_to_response('cog/project/index_form.html', 
                                      {'index': index, 'title': 'Update Site Index', 'project': project,
                                       'errors': errors},
                                      context_instance=RequestContext(request))


# method to update an existing project
@login_required
def project_update(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
            
    # limit to local projects only
    if not project.isLocal():
        return HttpResponseForbidden(LOCAL_PROJECTS_ONLY_MESSAGE)
            
    # check permission
    if not userHasAdminPermission(request.user, project) and not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method == 'GET':
        
        # create project tabs if not existing already
        # (because new tabs were added after the project was initialized)
        tabs = get_or_create_project_tabs(project)  # save=True
        
        # retrieve top-level subfolders
        folders = getTopSubFolders(project)
        
        # create form object from model
        form = ProjectForm(instance=project)
        return render_to_response('cog/project/project_form.html', 
                                  {'form': form, 'title': 'Update Project', 'project': project, 'action': 'update',
                                   'tabs': tabs, 'folders': folders, 'NAVMAP': NAVMAP, 'INVNAVMAP': INVNAVMAP},
                                  context_instance=RequestContext(request))
    
    else:
        
        # previous project state
        _active = project.active

        # update project instance (from database) form data
        form = ProjectForm(request.POST, request.FILES, instance=project)

        if (form.is_valid()):
                        
            # save the project
            project = form.save()
            
            # delete logo?
            if form.cleaned_data.get('delete_logo') == True:
                project.logo.delete()
            
            # initialize project ?
            if not project.isInitialized():
                initProject(project)  
                            
            # update project tabs, persist state
            setActiveProjectTabs(project.tabs.all(), request, save=True)
            
            # create folders with appropriate state
            createOrUpdateProjectSubFolders(project, request)
            
            # notify creator when the project is enabled (i.e. is switched from inactive to active)
            if not _active and project.active:                            
                notifyAuthorOfProjectApproval(project, request)
                        
            # redirect to project home (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('project_home', args=[project.short_name.lower()]))

        else:
            print 'Form is invalid %s' % form.errors
            
            # update project tabs, but do not persist state since form had errors
            tabs = get_or_create_project_tabs(project, save=False)
            # set active state of project tabs from HTTP parameters 
            for tablist in tabs:
                setActiveProjectTabs(tablist, request, save=False)
                
            folders = getTopSubFolders(project)
            
            return render_to_response('cog/project/project_form.html', 
                                      {'form': form, 'title': 'Update Project', 'project': project, 'action': 'update',
                                       'tabs': tabs, "folders": folders,
                                       'NAVMAP': NAVMAP, 'INVNAVMAP': INVNAVMAP},
                                      context_instance=RequestContext(request))
            
# method to update an existing project


@login_required
def project_delete(request, project_short_name):
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # limit to local projects only
    if not project.isLocal():
        return HttpResponseForbidden(LOCAL_PROJECTS_ONLY_MESSAGE)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if (request.method == 'GET'):
        return render_to_response('cog/project/project_delete.html', 
                                  {'project': project, 'title': 'Delete Project'},
                                  context_instance=RequestContext(request))
    else:
        
        # delete all project objects
        deleteProject(project)
        
        # redirect to admin index
        return HttpResponseRedirect(reverse('site_home'))


def contactus_display(request, project_short_name):
    """
    View to display the project "Contact Us" page.
    :param request:
    :param project_short_name:
    :return:

    """
        
    tab = TABS["CONTACTUS"]
    template_page = 'cog/project/_project_contactus.html'
    template_title = TAB_LABELS[tab]
    template_form_pages = {reverse("contactus_update", args=[project_short_name]): 'Contact Us'}
    return templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages)    


@login_required
def contactus_update(request, project_short_name):
    """
    View to update the project "Contact Us" metadata.
    """
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # GET request
    if request.method == 'GET':
        
        # create form object from model
        form = ContactusForm(instance=project)
        
        # display form view
        return render_contactus_form(request, project, form)
    
    # POST
    else:
        # update existing database model with form data
        form = ContactusForm(request.POST, instance=project)

        if form.is_valid():
            
            # save form data
            project = form.save()           
            
            # redirect to contact us display (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('contactus_display', args=[project.short_name.lower()]))
            
        else:
            # re-display form view
            if not form.is_valid():
                print 'Form is invalid  %s' % form.errors
            return render_contactus_form(request, project, form)

def render_contactus_form(request, project, form):
    return render_to_response('cog/project/contactus_form.html', 
                              {'form': form, 'title': 'Update Project Contact Us', 'project': project},
                              context_instance=RequestContext(request))
    
# method to delete a project and all its associated groups, permissions
def deleteProject(project):
    
    print "Deleting project: %s" % project.short_name
    
    # note: project posts and tabs are automatically deleted because of one-to-many relationship to project
        
    # delete permissions
    # note: if permissions didn't exit, they would be created first, then deleted
    project.getUserPermission().delete()
    project.getAdminPermission().delete()
    
    # delete groups
    # note: if groups didn't exit, they would be created first, then deleted
    project.getUserGroup().delete()
    project.getAdminGroup().delete()
            
    # delete project
    project.delete()


# function to notify the site administrators that a new project has been requested
def notifySiteAdminsOfProjectRequest(project, request):
    
    url = reverse('project_update', kwargs={ 'project_short_name':project.short_name.lower() })
    url = request.build_absolute_uri(url)
    subject = "New Project Registration Request"
    message = "User: %s has requested to register the new project: %s.\nPlease process the registration request at: %s ." \
            % (request.user.username, project.short_name, url)
    for admin in getSiteAdministrators():
        notify(admin, subject, message)


# function to notify a project creator that the project has been enabled
def notifyAuthorOfProjectApproval(project, request):
    if project.author:
        url = project.home_page_url()
        url = request.build_absolute_uri(url)
        subject = "New Project Registration Confirmation"
        message = "Congratulations, the project you requested: %s has been approved by the site administrator(s).\n" \
                  "The project home page is: %s" \
                  % (project.short_name, url)
        notify(project.author, subject, message)
    
# method to initialize a project by creating all objects associated with a project
# note that the project object has been already created (and persisted) from the form data
# also, note that the project tabs have already been persisted according to the selection expressed at creation


def initProject(project):
    
    print "Initializing project: %s" % project.short_name
                        
    # create project home page
    create_project_home(project, project.author)
    
    # create project groups
    uGroup = project.getUserGroup()
    aGroup = project.getAdminGroup()
    
    # create project permissions
    uPermission = project.getUserPermission()
    aPermission = project.getAdminPermission()
    
    # assign creator as project administrator
    if project.author is not None:
        addMembership(project.author, aGroup)
    
    # configure the project search with the default behavior
    create_project_search_profile(project)
    
    # create project index
    init_site_index(project)
    
    # create top-level bookmarks folder, needed to add a resource from any page
    folder = getTopFolder(project)
    
    # create default sub-folders
    createOrUpdateProjectSubFolders(project)
    
    # create images upload directory
    create_upload_directory(project)        


def development_display(request, project_short_name):
   
    tab = TABS["DEVELOPERS"] 
    template_page = 'cog/project/_project_developers.html'
    template_form_pages = {reverse('development_update', args=[project_short_name]): "Development"}
    template_title = "Development Overview"
   
    return templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages)


def software_display(request, project_short_name):
   
    tab = TABS["SOFTWARE"] 
    template_page = 'cog/project/_project_software.html'
    template_form_pages = {reverse('software_update', args=[project_short_name]): "Software"}
    template_title = "Software"
   
    return templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages)


def users_display(request, project_short_name):
   
    tab = TABS["USERS"] 
    template_page = 'cog/project/_project_users.html'
    template_form_pages = {reverse('users_update', args=[project_short_name]): "Getting Started"}
    template_title = "Getting Started"
   
    return templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages)


@login_required
def tags_update(request, project_short_name):
    """
    This creates the list of tags in the new tag form.

    :param request: A request for something.
    :type request: :class:`django.http.request.HttpRequest`
    :param str project_short_name: The name of the project.
    :returns: a constructed ProjectTagForm populated with tags associated with the project.
    :rtype: ProjectTagForm
    :raises: ...
    """

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
            
    # GET request
    if request.method == 'GET':

        # sorting of the tags occurs in the form itself in the _init_ function
        # populate the form with the list of tags associated with this project...they are highlighted.
        # that is project.tags.all().  All tags in the system are ProjectTags.objects.all().
        form = ProjectTagForm(initial={'tags': project.tags.all()})
        return render_tags_form(request, project, form)
        
    else:
        
        # create form from POST data
        form = ProjectTagForm(request.POST)
        
        # validate formset
        if form.is_valid():
                            
            # empty list of project tags                  
            project.tags = [] 
                        
            # fill list with tags from the DB
            for tag in form.cleaned_data['tags']:
                project.tags.add(tag)            
                       
            # associate new tag to project, save
            if len(form.cleaned_data['name'].strip()) > 0:
                tag = form.save()
                project.tags.add(tag)

            # save new list of project tags
            project.save()   
            
            # remove unused tags
            for tag in ProjectTag.objects.all():
                if len(tag.projects.all()) == 0:
                    tag.delete()
            
            # redirect to project home (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('project_home', args=[project.short_name.lower()]))
            
        else:
            print 'Form is invalid  %s' % form.errors
            return render_tags_form(request, project, form)


def project_empty_browser(request, tab):
    """
    View invoked when project browser is displayed outside of a project context.
    """
        
    return project_browser(request, '', tab)


def project_browser(request, project_short_name, tab):
    
    # optional tag filter
    tag = request.GET.get('tag', None)
            
    # retrieve project from database
    #project = get_object_or_404(Project, short_name__iexact=project_short_name)
    try:
        project = Project.objects.get(short_name__iexact=project_short_name)
    except ObjectDoesNotExist:
        project=None
        
    #print 'Project Browser project=%s tab=%s tag=%s user=%s' % (project, tab, tag, request.user)

    html = ''    
    if tab == 'this':
        if project is not None:
            # object that keeps track of successful invocations, if necessary
            display = DisplayStatus(True)  # open all sub-widgets by default
            html += makeProjectBrowser(project, tab, tag, request.user, 'Parent', 'parent_projects', display)
            html += makeProjectBrowser(project, tab, tag, request.user, 'Peer', 'peer_projects', display)
            html += makeProjectBrowser(project, tab, tag, request.user, 'Child', 'child_projects', display)
        else:
            html += '<div id="this_projects" style="display:block; padding:3px"><i>No projects found.</i></div>'
    elif tab == 'all':
        html += makeProjectBrowser(project, tab, tag, request.user, None, 'all_projects', None)
    elif tab == 'my':
        if not request.user.is_anonymous():
            html += makeProjectBrowser(project, tab, tag, request.user, None, 'my_projects', None)
        else:
            html += '<div id="tags_projects" style="display:block; padding:3px"><i>Please login to display your projects.</i></div>'
    elif tab == 'tags':
        if not request.user.is_anonymous():
            display = DisplayStatus(True)  # open all sub-widgets by default
            # loop over user tags (sorted by name)
            utags = request.user.profile.tags.all()
            if len(utags)>0:
                for utag in sorted(utags, key=lambda x: x.name):
                    #if tag==None or utag.name==tag:
                    html += makeProjectBrowser(project, tab, tag, request.user, utag.name, '%s_projects' % utag.name, display, addDeleteLink=True)
            else:
                html += '<div id="tags_projects" style="display:block; padding:3px"><i>No projects found.</i></div>'
        else:
            html += '<div id="tags_projects" style="display:block; padding:3px"><i>Please login to display your projects.</i></div>'
            
    return HttpResponse(html, content_type="text/html")

@login_required
def save_user_tag(request):
    
    # POST: when local user submits form, GET: when remote user is redirected to this site
    if request.method=='POST' or request.method=='GET':
        
        # retrieve tag
        tagName = request.REQUEST['tag']
        redirect = request.REQUEST['redirect']
        print 'Saving user tag: %s' % tagName
        print 'Eventually redirecting to: %s' % redirect
        
        if isUserLocal(request.user):
            try:
                tag = ProjectTag.objects.get(name__iexact=tagName)
                
                # add this tag to the user preferences
                utags = request.user.profile.tags
                if not tag in utags.all():
                    utags.add(tag)
                    request.user.profile.save()
                    print 'Tag: %s added to user: %s' % (tagName, request.user)
        
            except ObjectDoesNotExist:
                print "Invalid project tag: %s" % tag
                
            return HttpResponseRedirect(redirect)
    
        # redirect request to user home site
        else:
            url = "http://%s%s?tag=%s&redirect=%s" % (request.user.profile.site.domain, reverse('save_user_tag'), tagName, redirect)
            print 'Redirecting save request to URL=%s' % url
            response = HttpResponseRedirect(url)
            # set cookie to force eventual reloading of user properties
            response.set_cookie('LAST_ACCESSED', '0',
                                expires = (datetime.datetime.now() + datetime.timedelta(days=3650)),
                                httponly=True)
            print 'set cookie'
            return response
        
    
@login_required
def delete_user_tag(request):
    
    # POST: when local user submits form, GET: when remote user is redirected to this site
    if request.method=='POST' or request.method=='GET':

        tagName = request.REQUEST['tag']
        redirect = request.REQUEST['redirect']
        print 'Deleting user tag: %s' % tagName
        print 'Eventually redirecting to: %s' % redirect
        
        if isUserLocal(request.user):
            try:
                tag = ProjectTag.objects.get(name__iexact=tagName)
                utags = request.user.profile.tags
                if tag in utags.all():
                    utags.remove(tag)
                    request.user.profile.save()
                    
            except ObjectDoesNotExist:
                print "Invalid project tag: %s" % tag
                
            return HttpResponseRedirect(redirect)
                
        # redirect request to user home site
        else:
            url = "http://%s%s?tag=%s&redirect=%s" % (request.user.profile.site.domain, reverse('delete_user_tag'), tagName, redirect)
            print 'Redirecting delete request to URL=%s' % url
            response = HttpResponseRedirect(url)
            # set cookie to force eventual reloading of user properties
            print 'set cookie'
            response.set_cookie('LAST_ACCESSED', '0',
                    expires = (datetime.datetime.now() + datetime.timedelta(days=3650)),
                    httponly=True)

            return response
    

# utility class to track the status of the browser widgets
class DisplayStatus:
    def __init__(self, _open):
        self.open = _open

    
# Utility method to create the HTML for the browse widget
# example: project='cog', tab='tags', tagName=None, user=..., 
# widgetName='MIP', widgetId='MIP_projects', displayStatus='open'
def makeProjectBrowser(project, tab, tagName, user, widgetName, widgetId, displayStatus, addDeleteLink=False):
           
    # retrieve tag, if requested
    tag = None
    tagError = None # keeps track of error in retrieving tag
    if tagName is not None:
        try:
            tag = ProjectTag.objects.get(name__iexact=tagName)
        except ObjectDoesNotExist:
            # store error associated with non-existing tag
            tagError = "Tag does not exist"
    
    # list projects to include in widget
    if tagError is None:
        projects = listBrowsableProjects(project, tab, tag, user, widgetName)
    # list no projects if the tag is invalid
    else:
        projects = Project.objects.none()
                
    # build accordion header
    html = ""
    #if len(projects)>0:
    #    widgetDisplay = 'block'
    if widgetName is not None:
        html += '<div class="project_browser_bar" id="%s_bar">' % widgetId
        if addDeleteLink:
            html += "<a href='javascript:deleteUserTag(\"%s\");' class='deletelink'>&nbsp;</a>" % widgetName
        if widgetName in ['Parent', 'Child', 'Peer']:
            html += '%s (%s) projects' % (widgetName, str(len(projects)) )
        else:
            html += '%s (%s)' % (widgetName, str(len(projects)) ) # shorter title            
        html += '</div>'
    
    # determine widget status (depending on previous invocations)
    display = 'block'
    if displayStatus is not None:
        if displayStatus.open and len(projects)>0:
            display = 'block'
            #displayStatus.open = False # close all following widgets
        else:
            display = 'none'

    html += '<div id="'+widgetId+'" style="display:'+display+'; margin-left:4px;">';  # height of individual project widgets
    if len(projects) == 0:
        if tagError is not None:
            html += "<i>"+tagError+"</i>"
        else:
            # special case: cannot retrieve list of projects for guest user
            if (tab=='my' or tab=='tags') and not user.is_authenticated():
                html += "<i>Please login to display your projects.</i>"
            else:
                html += "<i>No projects found.</i>"
    else:     
        # loop over projects sorted by name
        for prj in sorted(projects, key=lambda prj: prj.short_name.lower()):
            #project_url = "http://%s%s" % (prj.site.domain, reverse('project_home', args=[prj.short_name.lower()]))
            html += '<a href="' + prj.getAbsoluteUrl() + '">' + prj.short_name + '</a><br/>'
    html += '</div>'

    # return both the HTML and the 'open' status of the following widget
    return html

# Utility method to list the projects for the browse widget
def listBrowsableProjects(project, tab, tag, user, widgetName):
            
    if tab == 'this':
        # note: reserved values for widget names
        if widgetName == 'Parent':
            projects = projectManager.listAssociatedProjects(project, 'parents')
        elif widgetName == 'Peer':
            projects = projectManager.listAssociatedProjects(project, 'peers')
        elif widgetName == 'Child':
            projects = projectManager.listAssociatedProjects(project, 'children')
            
    elif tab == 'all':
        #projects = Project.objects.filter(active=True)
        projects = projectManager.listAllProjects()
        
    elif tab == 'my':
        # retrieve all active projects for this user
        projects = getProjectsForUser(user, False)  # includePending==False
    elif tab == 'tags':
        if not user.is_authenticated():
            projects = Project.objects.none()
        else:
            # widgetName==user tag name
            utag = ProjectTag.objects.get(name=widgetName)
            projects = utag.projects.all()
            
    # filter projects
    _projects = []  # empty list
    for prj in projects:

        prjtags = list(prj.tags.all())
        if prj.isRemoteAndDisabled():
            # filter out projects from peer sites that are NOT enabled
            pass
        elif not prj.active:
            # do not add
            pass
        # only display projects that are visible to the user ?
        elif prj.isNotVisible(user):
            # do not add
            pass
        # don't apply the additional 'tag' filter to the 'tags' tab
        elif tab != 'tags' and tag is not None and tag not in prjtags:
            # do not add
            pass
        else:
            _projects.append(prj)
    
    return _projects


def render_tags_form(request, project, form):
    
    return render_to_response('cog/project/project_tags_form.html', 
                              {'form': form,
                               'title': 'Update Tags for Project: %s' % project.short_name,
                               'project': project},
                              context_instance=RequestContext(request))


@login_required
def development_update(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # GET request
    if request.method == 'GET':
                
        # create form object from model
        form = DevelopmentOverviewForm(instance=project)

        # render form
        return render_development_form(request, project, form)
    
    # POST request
    else:
        
        # update object from form data
        form = DevelopmentOverviewForm(request.POST, instance=project)
        
        # validate form data
        if form.is_valid():
            
            # persist changes
            project = form.save()
            
            # redirect to development overview (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('development_display', args=[project.short_name.lower()]))            
            
        # return to form
        else:
            print 'Form is invalid %s' % form.errors
            return render_development_form(request, project, form)


@login_required
def software_update(request, project_short_name):
    
    formClass = SoftwareForm
    form_template = 'cog/project/software_form.html'
    form_template_title = 'Software Update'
    display_view = 'software_display'
    return _project_page_update(request, project_short_name, formClass, form_template, form_template_title,
                                display_view)


@login_required
def users_update(request, project_short_name):
    
    formClass = UsersForm
    form_template = 'cog/project/users_form.html'
    form_template_title = 'Getting Started Update'
    display_view = 'users_display'
    return _project_page_update(request, project_short_name, formClass, form_template, form_template_title,
                                display_view)


@login_required
def _project_page_update(request, project_short_name, 
                         formClass, form_template, form_template_title, display_view):
    """Generic view for updating some project fields."""
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # GET request
    if request.method == 'GET':
                
        # create form object from model
        form = formClass(instance=project)

        # render form    
        return render_to_response(form_template,
                                  {'title': form_template_title, 'project': project, 'form': form},
                                  context_instance=RequestContext(request))
    
    # POST request
    else:
        
        # update object from form data
        form = formClass(request.POST, instance=project)
        
        # validate form data
        if form.is_valid():
            
            # persist changes
            project = form.save()
            
            # redirect to development overview (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse(display_view, args=[project.short_name.lower()]))            
            
        # return to form
        else:
            print 'Form is invalid %s' % form.errors
            return render_to_response(form_template,
                                      {'title': form_template_title, 'project': project, 'form': form},
                                      context_instance=RequestContext(request))

        
def render_development_form(request, project, form):
    return render_to_response('cog/project/development_form.html',
                              {'title' : 'Development Overview Update', 'project': project, 'form':form},
                               context_instance=RequestContext(request))