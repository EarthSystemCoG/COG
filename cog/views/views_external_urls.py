from django.shortcuts import get_object_or_404, render_to_response
from cog.models import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from cog.forms import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse  
from django.forms.models import modelformset_factory
from constants import PERMISSION_DENIED_MESSAGE
from cog.models.constants import *
from views_project import getProjectNotActiveRedirect, getProjectNotVisibleRedirect
from cog.models.navbar import TABS
from cog.models.external_url_page import EXTERNAL_URL_PAGES, EXTERNAL_URL_PAGE_MAP

# View to display the project roadmap.
def roadmap_display(request, project_short_name):
     
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Roadmap'
    template_form_pages = { reverse('roadmap_update', args=[project_short_name]) : template_name }
    return _external_urls_display(request, project_short_name, "URL_TYPE_ROADMAP", template_page, template_name, template_form_pages)

# Generic view to display a given type of external URLs.
def external_urls_display(request, project_short_name, suburl):
                          #external_url_type, 
                          #template_title, template_form_pages):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check project is active
    if project.active==False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)
    
    try:
        externalUrlPage = EXTERNAL_URL_PAGE_MAP[suburl]
    except KeyError:
        raise Exception("URL: %s is not properly configured" % request.path)
    
    external_url_type = externalUrlPage.type
    template_title = externalUrlPage.label
    template_form_page = "%s_update" % suburl
    template_form_pages = { reverse(template_form_page, args=[project_short_name, suburl]) : template_title }
    
    # build list of children with external urls of this type
    children = []
    for child in project.children():
        if len(child.get_external_urls(external_url_type)) > 0 and child.isVisible(request.user):
            children.append(child)
    
    # build list of peers with with external urls of this type
    peers = []
    for peer in project.peers.all():
        if len(peer.get_external_urls(external_url_type)) > 0 and peer.isVisible(request.user):
            peers.append(peer)
            
    return render_to_response('cog/common/rollup.html', 
                              {'project': project, 
                               'title': '%s %s' % (project.short_name, template_title), 
                               'template_page': 'cog/project/_external_urls_list.html', 
                               'template_title': template_title, 
                               'template_form_pages':template_form_pages,
                               'children':children, 'peers':peers,
                               'external_url_type':external_url_type },
                              context_instance=RequestContext(request))
    
# Generic view to display a given type of external URLs.
def _external_urls_display(request, project_short_name, external_url_type, 
                          template_page, template_title, template_form_pages):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check project is active
    if project.active==False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)

    
    # build list of children with external urls of this type
    children = []
    for child in project.children():
        if len(child.get_external_urls(external_url_type)) > 0 and child.isVisible(request.user):
            children.append(child)
    
    # build list of peers with with external urls of this type
    peers = []
    for peer in project.peers.all():
        if len(peer.get_external_urls(external_url_type)) > 0 and peer.isVisible(request.user):
            peers.append(peer)
            
    return render_to_response('cog/common/rollup.html', 
                              {'project': project, 
                               'title': '%s %s' % (project.short_name, template_title), 
                               'template_page': template_page, 
                               'template_title': template_title, 
                               'template_form_pages':template_form_pages,
                               'children':children, 'peers':peers,
                               'external_url_type':external_url_type },
                              context_instance=RequestContext(request))

# View to update the project roadmap
@login_required
def roadmap_update(request, project_short_name):
    
    type = "URL_TYPE_ROADMAP"
    redirect = reverse('roadmap_display', args=[project_short_name])
    return _external_urls_update(request, project_short_name, type, redirect)

# View to update the project policies
@login_required
def policies_update(request, project_short_name):
    
    type = "URL_TYPE_POLICY"
    tab = TABS["POLICIES"]
    redirect = reverse('governance_display', args=[project_short_name, tab])
    return _external_urls_update(request, project_short_name, type, redirect)

# Generic view to update external URLs
@login_required
def external_urls_update(request, project_short_name, suburl):
    
    # load user from session, project from HTTP request
    user = request.user
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasUserPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    try:
        externalUrlPage = EXTERNAL_URL_PAGE_MAP[suburl]
    except KeyError:
        raise Exception("URL: %s is not properly configured" % request.path)
    type = externalUrlPage.type
    redirect = reverse('%s_display' % suburl, args=[project_short_name, suburl])
    
    # number of empty instances to be displayed
    # exclude fields 'project', 'type' so they don't get validated
    # allow for instances to be deleted
    nextras = 1
    ExternalUrlFormSet = modelformset_factory(ExternalUrl, extra=nextras, exclude=('project','type'), can_delete=True,
                                              #widgets={'description': Textarea(attrs={'rows': 4})} ) # not working
                                              formfield_callback=custom_field_callback)
    
    # GET
    if request.method=='GET':
        
        # create formset instance backed by current saved instances
        # must provide the initial data to all the extra instances, 
        # which come in the list after the database instances
        #queryset = ExternalUrl.objects.filter(project=project, type=type)
        #initial_data = [ {'project':project, 'type':type } for count in xrange(len(queryset)+nextras)]
        #formset = ExternalUrlFormSet(queryset=queryset,initial=initial_data)   
        formset = ExternalUrlFormSet(queryset=ExternalUrl.objects.filter(project=project, type=type))
        
        return render_external_urls_form(request, project, formset, externalUrlPage, redirect)
    
    # POST
    else:
        
        formset = ExternalUrlFormSet(request.POST)
        
        if formset.is_valid():
            # select instances that have changed, don't save to database yet
            instances = formset.save(commit=False)
            for instance in instances:
                instance.project = project
                instance.type = type
                instance.save()
            return HttpResponseRedirect(redirect)
        
        else:
            print formset.errors
            return render_external_urls_form(request, project, formset, externalUrlPage, redirect)

# Generic view to update external URLs
@login_required
def _external_urls_update(request, project_short_name, type, redirect):
    
    # load user from session, project from HTTP request
    user = request.user
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasUserPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # number of empty instances to be displayed
    # exclude fields 'project', 'type' so they don't get validated
    # allow for instances to be deleted
    nextras = 1
    ExternalUrlFormSet = modelformset_factory(ExternalUrl, extra=nextras, exclude=('project','type'), can_delete=True,
                                              #widgets={'description': Textarea(attrs={'rows': 4})} ) # not working
                                              formfield_callback=custom_field_callback)
    
    # GET
    if request.method=='GET':
        
        # create formset instance backed by current saved instances
        # must provide the initial data to all the extra instances, 
        # which come in the list after the database instances
        #queryset = ExternalUrl.objects.filter(project=project, type=type)
        #initial_data = [ {'project':project, 'type':type } for count in xrange(len(queryset)+nextras)]
        #formset = ExternalUrlFormSet(queryset=queryset,initial=initial_data)   
        formset = ExternalUrlFormSet(queryset=ExternalUrl.objects.filter(project=project, type=type))
        
        return render_external_urls_form(request, project, formset, type, redirect)
    
    # POST
    else:
        
        formset = ExternalUrlFormSet(request.POST)
        
        if formset.is_valid():
            # select instances that have changed, don't save to database yet
            instances = formset.save(commit=False)
            for instance in instances:
                instance.project = project
                instance.type = type
                instance.save()
            return HttpResponseRedirect(redirect)
        
        else:
            print formset.errors
            return render_external_urls_form(request, project, formset, type, redirect)

# function to customize the widget used by specific formset fields
def custom_field_callback(field):
    if field.name == 'description':
        return field.formfield(widget=Textarea(attrs={'rows': 4}))
    else:
        return field.formfield()
     
def render_external_urls_form(request, project, formset, externalUrlPage, redirect):
     return render_to_response('cog/project/external_urls_form.html',
                              {'project':project, 'formset':formset, 'title' : '%s Update' % externalUrlPage.label, 
                               'type' : externalUrlPage.type, 'redirect':redirect },
                                context_instance=RequestContext(request))