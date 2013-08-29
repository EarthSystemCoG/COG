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
from cog.models.constants import TABS

# View to display the project trackers.
def trackers_display(request, project_short_name):
    
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Trackers'
    template_form_pages = { reverse('trackers_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_TRACKER, template_page, template_name, template_form_pages)

# View to display the project use cases.
def usecases_display(request, project_short_name):
    
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Use Cases'
    template_form_pages = { reverse('usecases_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_USECASE, template_page, template_name, template_form_pages)

def developer_guide_display(request, project_short_name):
    
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Developer\'s Guide'
    template_form_pages = { reverse('developer_guide_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_DEVELOPER_GUIDE, template_page, template_name, template_form_pages)

def design_docs_display(request, project_short_name):
    
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Design Documents'
    template_form_pages = { reverse('design_docs_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_DESIGN_DOC, template_page, template_name, template_form_pages)

def testing_display(request, project_short_name):
    
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Testing'
    template_form_pages = { reverse('testing_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_TESTING, template_page, template_name, template_form_pages)

def checklist_display(request, project_short_name):
    
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Checklist'
    template_form_pages = { reverse('checklist_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_CHECKLIST, template_page, template_name, template_form_pages)

# View to display the project code URLs.
def repositories_display(request, project_short_name):
        
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Repositories'
    template_form_pages = { reverse('repositories_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_REPOSITORY, template_page, template_name, template_form_pages)

# View to display the project roadmap.
def roadmap_display(request, project_short_name):
     
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Roadmap'
    template_form_pages = { reverse('roadmap_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_ROADMAP, template_page, template_name, template_form_pages)

# View to display the project download page.
def download_display(request, project_short_name):
     
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Download / Releases'
    template_form_pages = { reverse('download_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_DOWNLOAD, template_page, template_name, template_form_pages)

# View to display the Administrator's Guide page.
def admin_guide_display(request, project_short_name):
     
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Administrator\'s Guide'
    template_form_pages = { reverse('admin_guide_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_ADMIN_GUIDE, template_page, template_name, template_form_pages)

# View to display the user FAQ page.
def faq_display(request, project_short_name):
         
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'FAQ'
    template_form_pages = { reverse('faq_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_FAQ, template_page, template_name, template_form_pages)

# View to display the User's Guide page.
def user_guide_display(request, project_short_name):
     
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'User\'s Guide'
    template_form_pages = { reverse('user_guide_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_USER_GUIDE, template_page, template_name, template_form_pages)

# View to display the user Code Examples page.
def code_examples_display(request, project_short_name):
     
    template_page = 'cog/project/_external_urls_list.html'
    template_name = 'Code Examples'
    template_form_pages = { reverse('code_examples_update', args=[project_short_name]) : template_name }
    return external_urls_display(request, project_short_name, TYPE_CODE_EXAMPLE, template_page, template_name, template_form_pages)

    
# Generic view to display a given type of external URLs.
# This view sub-selects the project peer and children that external URLs of that type, 
# so that the page can render the widgets only if the URLs are found.
def external_urls_display(request, project_short_name, external_url_type, 
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
    
# View to update the project trackers
@login_required
def trackers_update(request, project_short_name):
    
    type = TYPE_TRACKER
    redirect = reverse('trackers_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project use cases
@login_required
def usecases_update(request, project_short_name):
    
    type = TYPE_USECASE
    redirect = reverse('usecases_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project software administrator's guide
@login_required
def admin_guide_update(request, project_short_name):
    
    type = TYPE_ADMIN_GUIDE
    redirect = reverse('admin_guide_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project code
@login_required
def repositories_update(request, project_short_name):
    
    type = TYPE_REPOSITORY
    redirect = reverse('repositories_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

@login_required
def developer_guide_update(request, project_short_name):
    
    type = TYPE_DEVELOPER_GUIDE
    redirect = reverse('developer_guide_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

@login_required
def design_docs_update(request, project_short_name):
    
    type = TYPE_DESIGN_DOC
    redirect = reverse('design_docs_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

@login_required
def testing_update(request, project_short_name):
    
    type = TYPE_TESTING
    redirect = reverse('testing_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

@login_required
def checklist_update(request, project_short_name):
    
    type = TYPE_CHECKLIST
    redirect = reverse('checklist_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project roadmap
@login_required
def roadmap_update(request, project_short_name):
    
    type = TYPE_ROADMAP
    redirect = reverse('roadmap_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project download page
@login_required
def download_update(request, project_short_name):
    
    type = TYPE_DOWNLOAD
    redirect = reverse('download_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project policies
@login_required
def policies_update(request, project_short_name):
    
    type = TYPE_POLICY
    tab = TABS["POLICIES"]
    redirect = reverse('governance_display', args=[project_short_name, tab])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project User's FAQ
@login_required
def faq_update(request, project_short_name):
        
    type = TYPE_FAQ
    tab = TABS["FAQ"]
    redirect = reverse('faq_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project User's Guide
@login_required
def user_guide_update(request, project_short_name):
    
    type = TYPE_USER_GUIDE
    tab = TABS["USER_GUIDE"]
    redirect = reverse('user_guide_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# View to update the project Code Examples
@login_required
def code_examples_update(request, project_short_name):
    
    type = TYPE_CODE_EXAMPLE
    tab = TABS["CODE_EXAMPLES"]
    redirect = reverse('code_examples_display', args=[project_short_name])
    return external_urls_update(request, project_short_name, type, redirect)

# Generic view to update external URLs
@login_required
def external_urls_update(request, project_short_name, type, redirect):
    
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
     
def render_external_urls_form(request, project, formset, type, redirect):
     return render_to_response('cog/project/external_urls_form.html', 
                              {'project':project, 'formset':formset, 'title' : '%s Update' % EXTERNAL_URL_DICT[type], 'type' : type, 'redirect':redirect },
                                context_instance=RequestContext(request))