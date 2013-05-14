'''
Module containing functionality for rendering templated pages.
'''

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from cog.models import Project, getLeadOrganizationalRoles, getMemberOrganizationalRoles
from cog.models.constants import TABS
from cog.models.utils import get_project_communication_means
from cog.views.constants import PERMISSION_DENIED_MESSAGE


def hasText(str):
    '''Utility function to establish whether a string has any non-empty characters.'''
    return str is not None and len(str.strip()) > 0

def _hasTemplatedInfo(project, tab):
    '''Utility function to determine whether a project has been populated 
       with the requested templated metadata, depending on type.'''
    
    if tab==TABS["ABOUTUS"]:
        # 'About Us' always populated with long_name, description
        return True
    elif tab==TABS["MISSION"] and hasText(project.mission) > 0:
        return True
    elif tab==TABS["VISION"] and hasText(project.vision) > 0:
        return True
    elif tab==TABS["VALUES"] and hasText(project.values) > 0:
        return True
    elif tab==TABS["PARTNERS"] and len(project.organization_set.all()) > 0:
        return True
    elif tab==TABS["SPONSORS"] and len(project.fundingsource_set.all()) > 0:
        return True   
    elif tab==TABS["PEOPLE"]:
        # "People" always populated with project users
        return True
    elif tab==TABS["CONTACTUS"] or tab==TABS["SUPPORT"]:
        # 'contactus' and 'support' always populated
        return True
    elif tab==TABS["DEVELOPMENT"] and hasText(project.developmentOverview):
        return True
    elif tab==TABS["GOVERNANCE"] and hasText(project.governanceOverview) > 0:     
         return True
    elif tab==TABS["BODIES"] and len(project.managementbody_set.all()) > 0:
         return True
    elif tab == TABS["ROLES"]:
        if len(getLeadOrganizationalRoles(project)) > 0 or len(getMemberOrganizationalRoles(project)) > 0:
            return True
    elif tab == TABS["COMMUNICATION"]:
        if len( get_project_communication_means(project, True) ) > 0:
            return True
    elif tab == TABS["PROCESSES"]:
        if hasText(project.taskPrioritizationStrategy) or hasText(project.requirementsIdentificationProcess):
            return True
    elif tab == TABS["POLICIES"]:
        if len(project.policies()) > 0:
            return True
    elif tab == TABS["GETINVOLVED"]:
        if len( get_project_communication_means(project, False) ) > 0:
            return True
    else:
        return False

def templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
        
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
   
    return render_templated_page(request, project, tab, template_page, template_title, template_form_pages, children, peers)

def render_templated_page(request, project, tab, template_page, template_title, template_form_pages, children, peers):
    return render_to_response('cog/common/rollup.html', 
                              {'project': project, 'title': '%s %s' % (project.short_name, template_title), 'tab' : tab,
                               'template_page': template_page, 'template_title': template_title, 'template_form_pages':template_form_pages,
                               'children':children, 'peers':peers },
                              context_instance=RequestContext(request))