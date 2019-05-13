from django.shortcuts import get_object_or_404, render
from cog.models import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from cog.forms import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.forms.models import modelformset_factory
from constants import PERMISSION_DENIED_MESSAGE
from cog.models.constants import *
from utils import getProjectNotActiveRedirect, getProjectNotVisibleRedirect
from cog.models.navbar import TABS
from cog.models.external_url_conf import externalUrlManager
from cog.models.auth import userHasContributorPermission


# Generic view to display a given type of external URLs.
def external_urls_display(request, project_short_name, suburl):
                          #external_url_type, 
                          #template_title, template_form_pages):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check project is active
    if project.active == False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)
    
    try:
        externalUrlConf = externalUrlManager.getConf(suburl=suburl)
    except KeyError:
        raise Exception("URL: %s is not properly configured" % request.path)
    
    external_url_type = externalUrlConf.type
    template_title = externalUrlConf.label
    template_form_page = "%s_update" % suburl
    template_form_pages = {reverse(template_form_page, args=[project_short_name, suburl]): template_title}
        
    # build list of children with external urls of this type
    children = _subSelectProjects(project.children(), externalUrlConf, request.user)
    
    # build list of peers with with external urls of this type
    peers = _subSelectProjects(project.peers.all(), externalUrlConf, request.user)

    # to change to tabbed rollups, load 'cog/common/rollup_tabbed.html'
    return render(request,
                  'cog/common/rollup_accordion.html',
                   {'project': project, 
                    'title': '%s %s' % (project.short_name, template_title),
                    # 'title': template_title,
                    'template_page': 'cog/project/_external_urls_list.html', 
                    'template_title': template_title, 
                    'template_form_pages': template_form_pages,
                    'children': children, 'peers': peers,
                    'external_url_type': external_url_type})


# method to sub-select related projects to display in external URL rollup
def _subSelectProjects(projects, externalUrlConf, user):
    
    _projects = []
    for proj in projects:
        if len(proj.get_external_urls(externalUrlConf.type)) > 0 and proj.isVisible(user):
            # only display rollup if corresponding tab is active
            projectTabsMap = proj.get_tabs_map()
            # tab for project must be active
            if externalUrlConf.suburl in projectTabsMap:
                tab = projectTabsMap[externalUrlConf.suburl]
                if tab.active:
                    _projects.append(proj)
            # no tab for project found
            else:
                _projects.append(proj)
    return _projects


# Generic view to update external URLs
@login_required
def external_urls_update(request, project_short_name, suburl):
    
    # load user from session, project from HTTP request
    user = request.user
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasContributorPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    try:
        externalUrlConf = externalUrlManager.getConf(suburl=suburl)
    except KeyError:
        raise Exception("URL: %s is not properly configured" % request.path)
    type = externalUrlConf.type

    redirect = reverse('%s_display' % suburl, args=[project_short_name, suburl])
    
    # number of empty instances to be displayed
    # exclude fields 'project', 'type' so they don't get validated
    # allow for instances to be deleted
    nextras = 1
    ExternalUrlFormSet = modelformset_factory(ExternalUrl, extra=nextras, exclude=('project', 'type'), can_delete=True,
                                              #widgets={'description': Textarea(attrs={'rows': 4})} ) # not working
                                              formfield_callback=custom_field_callback)
    
    # GET
    if request.method == 'GET':

        # create formset instance backed by current saved instances
        # must provide the initial data to all the extra instances, 
        # which come in the list after the database instances

        # if template is release schedules or prioritization, which are dates, reverse order of the urls
        # sorting of the view occurs in models/project.py/get_external_urls()
        if type == 'release_schedule':
            formset = ExternalUrlFormSet(queryset=ExternalUrl.objects.filter(project=project, type=type).
                                         order_by('-title'))

        elif type == 'prioritization':
            formset = ExternalUrlFormSet(queryset=ExternalUrl.objects.filter(project=project, type=type).
                                         order_by('-title'))
        else:

            # external_urls are ordered by title when editing to match the order when just viewing.
            formset = ExternalUrlFormSet(queryset=ExternalUrl.objects.filter(project=project, type=type).
                                         order_by('title'))

        return render_external_urls_form(request, project, formset, externalUrlConf, redirect)
    
    # POST
    else:
        formset = ExternalUrlFormSet(request.POST)

        if formset.is_valid():
            # select instances that have changed, don't save to database yet
            instances = formset.save(commit=False)
            # must manually delete the instances marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            # for all others, assign the project reference and persist changes
            for instance in instances:
                instance.project = project
                instance.type = type
                instance.save()
            return HttpResponseRedirect(redirect)
        
        else:
            return render_external_urls_form(request, project, formset, externalUrlConf, redirect)


# function to customize the widget used by specific formset fields
def custom_field_callback(field):
    if field.name == 'description':
        return field.formfield(widget=Textarea(attrs={'rows': 4}))
    else:
        return field.formfield()


def render_external_urls_form(request, project, formset, externalUrlConf, redirect):
    return render(request,
                  'cog/project/external_urls_form.html',
                  {'project':project, 'formset':formset, 'title' : '%s Update' % externalUrlConf.label, 
                   'type' : externalUrlConf.type, 'redirect': redirect })