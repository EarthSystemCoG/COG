from cog.forms import *
from cog.models import *
from cog.models.constants import LEAD_ORGANIZATIONAL_ROLES_DICT, \
    ROLE_CATEGORY_LEAD, ROLE_CATEGORY_MEMBER, MANAGEMENT_BODY_CATEGORY_STRATEGIC, \
    MANAGEMENT_BODY_CATEGORY_OPERATIONAL
from constants import PERMISSION_DENIED_MESSAGE
from django.contrib.auth.decorators import login_required
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils.functional import curry
from utils import getProjectNotActiveRedirect, getProjectNotVisibleRedirect
from cog.models.navbar import TABS, TAB_LABELS
from cog.views.views_templated import templated_page_display
from cog.models.auth import userHasAdminPermission
import logging

log = logging.getLogger(__name__)
# management_body_update proj.short_name.lower category


def governance_display(request, project_short_name, tab):
    """
    :param request:
    :param project_short_name:
    :param tab:
    :return:
    Dispatcher for display of governance pages.
    """
    
    template_page = 'cog/governance/_governance.html'
    template_title = TAB_LABELS[tab]
    if tab == TABS["GOVERNANCE"]:
        template_title = 'Governance Overview'
        template_form_pages = {reverse("governance_overview_update", args=[project_short_name]): 'Governance Overview'}
    elif tab == TABS["BODIES"]:
        template_form_pages = {reverse("management_body_update", args=[project_short_name, 'Strategic']):
                               'Strategic Bodies', reverse("management_body_update", args=[project_short_name,
                               'Operational']): 'Operational Bodies'}
    elif tab == TABS["ROLES"]:
        template_form_pages = {reverse("organizational_role_update", args=[project_short_name]): 'Roles'}
    elif tab == TABS["PROCESSES"]:
        template_form_pages = {reverse("governance_processes_update", args=[project_short_name]): 'Processes'}
    elif tab == TABS["COMMUNICATION"]:
        template_form_pages = {reverse("communication_means_update", args=[project_short_name]): 'Communications'}
    return templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages)


# view to update the project Management Body objects
@login_required
def management_body_update(request, project_short_name, category):
    
    # initialize ManagementBodyPurpose choices
    if len(ManagementBodyPurpose.objects.all()) == 0:
        initManagementBodyPurpose()
        
    # use different forms to limit selection of ManagementBodyPurpose
    if category == MANAGEMENT_BODY_CATEGORY_STRATEGIC:
        objectTypeForm = StrategicManagementBodyForm
        formsetType = StrategicManagementBodyInlineFormset
    else:
        objectTypeForm = OperationalManagementBodyForm
        formsetType = OperationalManagementBodyInlineFormset
    
    # delegate to view for generic governance object
    tab = TABS["BODIES"]
    redirect = HttpResponseRedirect(reverse('governance_display', args=[project_short_name.lower(), tab]))
    return governance_object_update(request, project_short_name, tab, ManagementBody, objectTypeForm, formsetType,
                                    '%s Management Bodies Update' % category, 'cog/governance/management_body_form.html'
                                    , redirect)


# view to update the project Communication Means objects
@login_required
def communication_means_update(request, project_short_name):
    
    tab = TABS["COMMUNICATION"]
    formsetType = InternalCommunicationMeansInlineFormset
    redirect = HttpResponseRedirect(reverse('governance_display', args=[project_short_name.lower(), tab]))

    # delegate to view for generic governance object
    return governance_object_update(request, project_short_name, tab, CommunicationMeans, CommunicationMeansForm,
                                    formsetType, 'Communications Update',
                                    'cog/governance/communication_means_form.html', redirect)

    
@login_required
def governance_overview_update(request, project_short_name):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # GET request
    if request.method == 'GET':
                
        # create form object from model
        form = GovernanceOverviewForm(instance=project)

        # render form
        return render_governance_overview_form(request, form, project)
    
    # POST request
    else:
        
        # update object from form data
        form = GovernanceOverviewForm(request.POST, instance=project)
        
        # validate form data
        if form.is_valid():
            
            # persist changes
            project = form.save()
            
            # redirect to governance display (GET-POST-REDIRECT)
            tab = 'governance'
            return HttpResponseRedirect(reverse('governance_display', args=[project.short_name.lower(), tab]))            
            
        # return to form
        else:
            log.debug('Form is invalid %s' % form.errors)
            return render_governance_overview_form(request, form, project)

    
# Subclass of BaseInlineFormset that is used to 
# sub-select the 'strategic' instances of ManagementBody specific to a given project
class StrategicManagementBodyInlineFormset(BaseInlineFormSet):
        
    def get_queryset(self):
        # standard BaseInlineFormSet that sub-selects by instance=project
        querySet = super(StrategicManagementBodyInlineFormset, self).get_queryset() 
        # additionally sub-select by category='Strategic'
        return querySet.filter(category='Strategic')


class OperationalManagementBodyInlineFormset(BaseInlineFormSet):
        
    def get_queryset(self):
        return super(OperationalManagementBodyInlineFormset, self).get_queryset().filter(category='Operational')


class InternalCommunicationMeansInlineFormset(BaseInlineFormSet):
    
    def get_queryset(self):
        return super(InternalCommunicationMeansInlineFormset, self).get_queryset().filter(internal=True)
    
        
# Generic view for updating a governance object.
#
# The object must have the following attributes and methods:
# obj.project
# obj.__unicode__
def governance_object_update(request, project_short_name, tab, objectType, objectTypeForm, formsetType, title, template,
                             redirect):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # initialize formset factory for this governance object
    ObjectFormSet = inlineformset_factory(Project, objectType, extra=1, form=objectTypeForm, formset=formsetType, fields="__all__")

    # GET request
    if request.method == 'GET':
        
        # create formset instance associated to current project
        formset = ObjectFormSet(instance=project)
        
        return render_governance_object_form(request, project, formset, title, template)

    # POST method
    else:
        # update formset from POST data
        formset = ObjectFormSet(request.POST, instance=project)
        
        if formset.is_valid():
            
            # save changes to database
            instances = formset.save()
                        
            # set additional object flags
            for instance in instances:
                dict = {}
                if formsetType == InternalCommunicationMeansInlineFormset:
                    dict['internal'] = True
                instance.set_category(dict=dict)
                instance.save()
                       
            # redirect to governance display (GET-POST-REDIRECT)
            return redirect
            
        else:
            log.debug('Formset is invalid  %s' % formset.errors)
            return render_governance_object_form(request, project, formset, title, template)
            

def render_governance_object_form(request, project, formset, title, template):
    return render(request,
                  template,
                  {'title': title, 'project': project, 'formset': formset})

# view to update a Communication Means object members  
@login_required
def communication_means_members(request, object_id):
    
    commnicationMeans = get_object_or_404(CommunicationMeans, pk=object_id)
    # create form class with current project
    #communicationMeansMemberForm = staticmethod(curry(CommunicationMeansMemberForm, project=commnicationMeans.project))
    
    # delegate to generic view with specific object types
    tab = TABS["COMMUNICATION"]
    redirect = reverse('governance_display', args=[commnicationMeans.project.short_name.lower(), tab])
    return members_update(request, tab, object_id, CommunicationMeans, CommunicationMeansMember, CommunicationMeansMemberForm, redirect)


# view to update an Organizational Role object members  
@login_required
def organizational_role_members(request, object_id):
    
    organizationalRole = get_object_or_404(OrganizationalRole, pk=object_id)

    # create form class with current project
    #organizationalRoleMemberForm = staticmethod(curry(OrganizationalRoleMemberForm, project=organizationalRole.project))
    
    # delegate to generic view with specific object types
    tab = TABS["ROLES"]
    redirect = reverse('governance_display', args=[organizationalRole.project.short_name.lower(), tab])
    return members_update(request, tab, object_id, OrganizationalRole, OrganizationalRoleMember, OrganizationalRoleMemberForm, redirect)


# view to update a Management Body object members
@login_required
def management_body_members(request, project_short_name, object_id):
    
    # retrieve object
    managementBody = get_object_or_404(ManagementBody, pk=object_id)
        
    # delegate to generic view with specific object types
    tab = TABS["BODIES"]
    redirect = reverse('governance_display', args=[managementBody.project.short_name.lower(), tab])
    return members_update(request, tab, object_id, ManagementBody, ManagementBodyMember, ManagementBodyMemberForm, redirect)
    
# 
# Generic view to update members for:
# -) objectType=CommunicationMeans, objectMemberType=CommunicationMeansMember
# -) objectType=ManagementBody, objectMemberType=ManagementBodyMember
#
# The object must have the following attributes and methods:
# obj.project
# obj.__unicode__
#
def members_update(request, tab, objectId, objectType, objectMemberType, objectMemberForm, redirect):
    
    # retrieve governance object
    obj = get_object_or_404(objectType, pk=objectId)
    
    # check permission
    if not userHasAdminPermission(request.user, obj.project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # formset factory
    users_queryset = projectUsersQuerySet(obj.project)
    ObjectFormSet = inlineformset_factory(objectType, objectMemberType, form=objectMemberForm, extra=3, fields="__all__")

    # GET request
    if request.method == 'GET':
        
        # retrieve current members
        formset = ObjectFormSet(instance=obj)
        for form in formset.forms:
            form.fields['user'].queryset = users_queryset
        
        # render view
        return render_members_form(request, obj, formset, redirect)
        
    # POST request
    else:
        formset = ObjectFormSet(request.POST, instance=obj)
        
        if formset.is_valid():
            
            # save updated members
            instances = formset.save()
            
            # redirect to display (GET-POST-REDIRECT)
            return HttpResponseRedirect(redirect)
                      
        else:
            log.debug('Formset is invalid: %s' % formset.errors)
            
            # redirect to form view
            return render_members_form(request, obj, formset, redirect)


def render_members_form(request, object, formset, redirect):
        
    return render(request,
                  'cog/governance/members_form.html',
                  {'title': '%s Members Update' % object,
                   'project': object.project,
                   'formset': formset, 'redirect': redirect})
    

@login_required
def processes_update(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # GET request
    if request.method == 'GET':
                
        # create form object from model
        form = GovernanceProcessesForm(instance=project)

        # render form
        return render_governance_processes_form(request, form, project)
    
    # POST request
    else:
        
        # update object from form data
        form = GovernanceProcessesForm(request.POST, instance=project)
        
        # validate form data
        if form.is_valid():
            
            # persist changes
            project = form.save()
            
            # redirect to governance display (GET-POST-REDIRECT)
            tab = 'processes'
            return HttpResponseRedirect(reverse('governance_display', args=[project.short_name.lower(), tab]))            
            
        # return to form
        else:
            log.debug('Form is invalid %s' % form.errors)
            return render_governance_processes_form(request, form, project)

def render_governance_processes_form(request, form, project):
    return render(request,
                  'cog/governance/governance_processes_form.html',
                  {'title': 'Governance Processes Update', 'project': project, 'form': form} )
    
def render_governance_overview_form(request, form, project):
    return render(request,
                  'cog/governance/governance_overview_form.html',
                  {'title': 'Governance Overview Update', 'project': project, 'form': form})


# Method to update an organizational role
@login_required
def organizational_role_update(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # must build the formset via non-traditional means to pass the current project as a class attribute
    OrganizationalRoleFormSet = inlineformset_factory(Project, OrganizationalRole, extra=1, can_delete=True,
                                                      form=OrganizationalRoleForm, fields="__all__")
    
    # GET request
    if request.method == 'GET':
        # create formset backed up by current saved instances
        organizational_role_formset = OrganizationalRoleFormSet(instance=project)
        
        # display form view
        return render_organizational_role_form(request, project, organizational_role_formset)
        
    # POST request
    else:
        organizational_role_formset = OrganizationalRoleFormSet(request.POST, instance=project)
        
        # validate formset
        if organizational_role_formset.is_valid():
            
            # save changes to databaase
            orgrole_instances = organizational_role_formset.save()
            
            # assign role category and save again
            for role in orgrole_instances:
                role.set_category()
                role.save()
            
            # redirect to governance display (GET-POST-REDIRECT)
            tab = 'roles'
            return HttpResponseRedirect(reverse('governance_display', args=[project.short_name.lower(), tab]))
            
        else:
            log.debug('Organizational Role formset is invalid: %s' % organizational_role_formset.errors)
            
            # redorect to form
            return render_organizational_role_form(request, project, organizational_role_formset)


def render_organizational_role_form(request, project, formset):
    return render(request,
                  'cog/governance/organizational_role_form.html',
                  {'title': 'Organizational Roles Update', 'project': project, 'formset': formset})
