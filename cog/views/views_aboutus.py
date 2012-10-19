from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.forms.models import modelformset_factory, inlineformset_factory
import string
import os
from django.conf import settings

from cog.models import *
from cog.forms import *
from cog.utils import *
from cog.notification import notify
from cog.services.membership import addMembership
from cog.models.utils import *

from constants import PERMISSION_DENIED_MESSAGE        

def aboutus_display(request, project_short_name, tab):
    ''' View to display an project tab page. '''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    template_page = 'cog/project/_project_aboutus.html'
    template_form_name = "aboutus_update"
    template_title = tab.capitalize()    
    children = project.children()
    peers = project.peers.all()
    return _templated_page_display(request, project, tab,
                                   template_page, template_title, template_form_name, children, peers)
    
def _hasTemplatedInfo(project, tab):
    '''Utility function to determine whether a project has been populated 
       with the requested templated metadata, depending on type.'''
    
    if (tab=='aboutus'):
        # 'About Us' always populated with long_name, description
        return True
    elif (tab=='mission') and project.mission is not None and len(project.mission.strip()) > 0:
        return True
    elif (tab=='vision') and project.vision is not None and len(project.vision.strip()) > 0:
        return True
    elif (tab=='values') and project.values is not None and len(project.values.strip()) > 0:
        return True
    elif (tab=='partners') and project.values is not None and len(project.organization_set.all()) > 0:
        return True
    elif (tab=='sponsors') and project.values is not None and len(project.fundingsource_set.all()) > 0:
        return True   
    elif (tab=='people'):
        # "People" always populated with project users
        return True
    else:
        return False

def _templated_page_display(request, project, tab, template_page, template_title, template_form_name, children, peers):
        
    # check project is active
    if project.active==False:
        return getProjectNotActiveRedirect(request, project)
    elif project.isNotVisible(request.user):
        return getProjectNotVisibleRedirect(request, project)
    
    # build list of children with relevant metadata that are visible to user
    children = []
    for child in project.children():
        if _hasTemplatedInfo(child, tab) and child.isVisible(request.user):
            children.append(child)
    
    # build list of peers with relevant metadata that are visible to user
    peers = []
    for peer in project.peers.all():
        if _hasTemplatedInfo(peer, tab) and peer.isVisible(request.user):
            peers.append(peer)
   
    return render_templated_page(request, project, tab, template_page, template_title, template_form_name, children, peers)

def render_templated_page(request, project, tab, template_page, template_title, template_form_name, children, peers):
    return render_to_response('cog/common/rollup.html', 
                              {'project': project, 'title': '%s %s' % (project.short_name, template_title), 'tab' : tab,
                               'template_page': template_page, 'template_title': template_title, 'template_form_name':template_form_name,
                               'children':children, 'peers':peers },
                              context_instance=RequestContext(request))

@login_required
def aboutus_update(request, project_short_name, tab):
    '''View to update the project "About Us" metadata.'''

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
        return render_aboutus_form(request, project, tab, form, organization_formset, fundingsource_formset)

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
            return HttpResponseRedirect(reverse('aboutus_display', args=[project.short_name.lower(), tab]))
            
        else:
            # re-display form view
            if not form.is_valid():
                print 'Form is invalid  %s' % form.errors
            if not organization_formset.is_valid():
                print 'Organization formset is invalid  %s' % organization_formset.errors
            if not fundingsource_formset.is_valid():
                print 'Funding Source formset is invalid  %s' % fundingsource_formset.errors
            return render_aboutus_form(request, project, tab, form, organization_formset, fundingsource_formset)

def render_aboutus_form(request, project, tab, form, organization_formset, fundingsource_formset):
    return render_to_response('cog/project/aboutus_form.html', 
                          {'form': form, 'tab':tab,
                           'organization_formset':organization_formset, 
                           'fundingsource_formset':fundingsource_formset,
                           'title': 'Update Project Details', 'project': project }, 
                          context_instance=RequestContext(request))