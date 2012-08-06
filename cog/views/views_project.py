from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.forms.models import modelformset_factory, inlineformset_factory
import string

from cog.models import *
from cog.forms import *
from cog.utils import *
from cog.notification import notify
from cog.services.membership import addMembership
from cog.models.utils import *

from constants import PERMISSION_DENIED_MESSAGE

# method to add a new project, with optional parent project
@login_required
def project_add(request):
    
    if (request.method=='GET'):
        
        project = Project(active=False, author=request.user)
        
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
        
        form = ProjectForm(instance=project)
        return render_to_response('cog/project/project_form.html',
                                  { 'form': form, 'title' : 'Register New Project', 'project': parent, 'action':'add', 'tabs':tabs },
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
            return render_to_response('cog/project/project_form.html', 
                                      {'form': form, 'title': 'Register New Project', 'action':'add', 'tabs':tabs },
                                      context_instance=RequestContext(request))
            
# method to reorganize the project index menu 
@login_required
def project_index(request, project_short_name):
    
    TOPIC_ID = "topic_id_"
    PAGE_ID = "_page_id_"
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
        
    # check permission
    if not userHasAdminPermission(request.user, project) and not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    errors = {}
    index = site_index(project)
    
    # GET
    if (request.method=='GET'):
        
        return render_to_response('cog/project/index_form.html', 
                                  {'index': index, 'title': 'Update Site Index', 'project':project, 'errors':errors },
                                  context_instance=RequestContext(request))
    # POST
    else:
        
        # retrieve current index, update according to form data
        index = site_index(project)
        # map (topic, new_order)
        topicMap = {} 
        valid = True # form data validation flag
        
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
                                  {'index': index, 'title': 'Update Site Index', 'project':project, 'errors':errors },
                                   context_instance=RequestContext(request))

    
# method to update an existing project
@login_required
def project_update(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
            
    # check permission
    if not userHasAdminPermission(request.user, project) and not request.user.is_staff:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if (request.method=='GET'):
        
        # create project tabs if not existing already
        # (because new tabs were added after the project was initialized)
        tabs = get_or_create_project_tabs(project) # save=True
        
        # create form object from model
        form = ProjectForm(instance=project)
        return render_to_response('cog/project/project_form.html', 
                                  {'form': form, 'title': 'Update Project', 'project': project, 'action':'update', 'tabs': tabs }, 
                                  context_instance=RequestContext(request))
    
    else:
        
        # previous project state
        _active = project.active

        # update project instance (from database) form data
        form = ProjectForm(request.POST, request.FILES, instance=project)

        if (form.is_valid()):
                        
            # save the project
            project = form.save()
            
            # delete logo ?
            if form.cleaned_data.get('delete_logo')==True:
                project.logo.delete()
            
            # initialize project ?
            if not project.isInitialized():
                initProject(project)  
                            
            # update project tabs, persist state
            setActiveProjectTabs(project.tabs.all(), request, save=True)
            
            # notify creator when the project is enabled (i.e. is switched from inactive to active)
            if not _active and project.active:                            
                notifyAuthorOfProjectApproval(project, request)
                        
            # redirect to project home (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('project_home', args=[project.short_name.lower()]))

        else:
            print 'Form is invalid %s' % form.errors
            
            # update project tabs, but do not persist state since form had errors
            tabs = setActiveProjectTabs(project.tabs.all(), request, save=False)
            
            return render_to_response('cog/project/project_form.html', 
                                      {'form': form, 'title': 'Update Project', 'project': project, 'action':'update', 'tabs': tabs }, 
                                       context_instance=RequestContext(request))
            
# method to update an existing project
@login_required
def project_delete(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if (request.method=='GET'):
        return render_to_response('cog/project/project_delete.html', 
                                  {'project': project, 'title': 'Delete Project' },
                                  context_instance=RequestContext(request))
    else:
        
        # delete all project objects
        deleteProject(project)
        
        # redirect to admin index
        return HttpResponseRedirect(reverse('site_index'))
    
def aboutus_display(request, project_short_name):
    ''' View to display the project "About Us" page. '''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    template_page = 'cog/project/_project_aboutus.html'
    template_title = 'About Us'
    children = project.children()
    peers = project.peers.all()
    return _templated_page_display(request, project, template_page, template_title, children, peers, children, peers)

def contactus_display(request, project_short_name):
    ''' View to display the project "Contact Us" page. '''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    template_page = 'cog/project/_project_contactus.html'
    template_title = 'Contact Us'
    children = project.children()
    peers = project.peers.all()
    return _templated_page_display(request, project, template_page, template_title, children, peers)

def support_display(request, project_short_name):
    ''' View to display the project "Support" page. '''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    template_page = 'cog/project/_project_support.html'
    template_title = 'Support'
    children = project.children()
    peers = project.peers.all()
    return _templated_page_display(request, project, template_page, template_title, children, peers)
    
def _templated_page_display(request, project, template_page, template_title, children, peers):
        
    # check project is active
    if project.active==False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)
    
    return render_templated_page(request, project, template_page, template_title, children, peers)

def render_templated_page(request, project, template_page, template_title, children, peers):
    return render_to_response('cog/project/project_rollup.html', 
                              {'project': project, 'title': '%s %s' % (project.short_name, template_title), 
                               'template_page': template_page, 'template_title': template_title,
                               'children':children, 'peers':peers },
                              context_instance=RequestContext(request))


# method to update the project details
@login_required
def aboutus_update(request, project_short_name):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # initialize formset factories for this project related objects
    OrganizationFormSet  = inlineformset_factory(Project, Organization, extra=1, can_delete=True)
    FundingSourceFormSet = inlineformset_factory(Project, FundingSource, extra=1, can_delete=True)
    
    # GET request
    if (request.method=='GET'):
        
        # create form object from model
        form = AboutusForm(instance=project)
        
        # create formset instances backed by current saved instances
        # assign a unix prefix to each formset to avoid colilsions
        organization_formset = OrganizationFormSet(instance=project, prefix='orgfs')
        fundingsource_formset = FundingSourceFormSet(instance=project, prefix='fundfs')
        
        # display form view
        return render_aboutus_form(request, project, form, organization_formset, fundingsource_formset)

    # POST request
    else:
        # update existing database model with form data
        form = AboutusForm(request.POST, instance=project)
        organization_formset = OrganizationFormSet(request.POST, instance=project, prefix='orgfs')
        fundingsource_formset = FundingSourceFormSet(request.POST, instance=project, prefix='fundfs')
        
        if form.is_valid() and organization_formset.is_valid() and fundingsource_formset.is_valid():
            # save project data
            project = form.save()           
            oinstances = organization_formset.save()
            fsinstances = fundingsource_formset.save()
            
            # redirect to about us display (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('aboutus_display', args=[project.short_name.lower()]))
            
        else:
            # re-display form view
            if not form.is_valid():
                print 'Form is invalid  %s' % form.errors
            if not organization_formset.is_valid():
                print 'Organization formset is invalid  %s' % organization_formset.errors
            if not fundingsource_formset.is_valid():
                print 'Funding Source formset is invalid  %s' % fundingsource_formset.errors
            return render_aboutus_form(request, project, form, organization_formset, fundingsource_formset)

def render_aboutus_form(request, project, form, organization_formset, fundingsource_formset):
    return render_to_response('cog/project/aboutus_form.html', 
                          {'form': form, 'organization_formset':organization_formset, 
                           'fundingsource_formset':fundingsource_formset,
                           'title': 'Update Project Details', 'project': project }, 
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
        message = "Congratulations, the project you requested: %s has been approved by the site administrator(s).\nThe project home page is: %s" \
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
    addMembership(project.author, aGroup)
    
    # configure the project search with the default behavior
    create_project_search_profile(project)
    
    # create project index
    init_site_index(project)
    
    # create top-level bookmarks folder
    folder = getTopFolder(project)
    
# method to set the state of the project tabs from the HTTP request parameters
# note: tabs is a list of tabs (not a list of lists of tabs)
def setActiveProjectTabs(tabs, request, save=False):
    
    for tab in tabs:
        # Home tab MUST always be active
        if tab.label.endswith("Home"):
            tab.active = True
        elif "tab_%s" % tab.label in request.POST.keys():
            tab.active = True
        else:
            tab.active = False
        if save:
            tab.save()
    return tabs

# function to return an error message if a project is not active
def getProjectNotActiveRedirect(request, project):
        messages = ['Access to all pages of project %s is currently forbidden.' % project.short_name,
                    'Please contact support for any questions.'] 
        return render_to_response('cog/common/message.html', 
                                  {'mytitle':'Project Access Not Enabled', 
                                   'project':project,
                                   'messages':messages }, 
                                  context_instance=RequestContext(request))
        
# function to return an error message if a project is not public
def getProjectNotVisibleRedirect(request, project):
        messages = ['Access to all pages of project %s is restricted to members only.' % project.short_name,
                    'Please contact support for any questions.'] 
        return render_to_response('cog/common/message.html', 
                                  {'mytitle':'Project Access Restricted', 
                                   'project':project,
                                   'messages':messages }, 
                                  context_instance=RequestContext(request))