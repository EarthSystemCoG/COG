from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.forms.models import modelformset_factory, inlineformset_factory
import string
import os
from django.conf import settings

from cog.models import *
from cog.models.auth import userHasContributorPermission, userHasAdminPermission
from cog.models.navbar import TABS, TAB_LABELS
from cog.models.constants import UPLOAD_DIR_LOGOS, UPLOAD_DIR_PHOTOS
from cog.forms import *
from cog.utils import *
from cog.notification import notify
from cog.models.utils import *
from cog.views.views_templated import templated_page_display
from cog.util.thumbnails import *
from cog.models.auth import userHasAdminPermission

from constants import PERMISSION_DENIED_MESSAGE

import logging

log = logging.getLogger(__name__)

def aboutus_display(request, project_short_name, tab):
    """
    View to display an project tab page.
    :param request:
    :param project_short_name:
    :param tab:
    :return:
    """

    template_page = 'cog/project/_project_aboutus.html'
    if tab == TABS["MISSION"]:
        template_form_pages = {reverse('aboutus_update', args=[project_short_name, tab]): 'Mission'}
    elif tab == TABS["VISION"]:
        template_form_pages = {reverse('aboutus_update', args=[project_short_name, tab]): 'Vision'}
    elif tab == TABS["VALUES"]:
        template_form_pages = {reverse('aboutus_update', args=[project_short_name, tab]): 'Values'}
    elif tab == TABS["IMPACTS"]:
        template_form_pages = {reverse('impacts_update', args=[project_short_name, tab]): 'Impacts'}
    elif tab == TABS["HISTORY"]:
        template_form_pages = {reverse('aboutus_update', args=[project_short_name, tab]): 'History'}
    elif tab == TABS["PARTNERS"]:
        template_form_pages = {reverse('partners_update', args=[project_short_name, tab]): 'Partners'}
    elif tab == TABS["SPONSORS"]:
        template_form_pages = {reverse('sponsors_update', args=[project_short_name, tab]): 'Sponsors'}
    elif tab == TABS["PEOPLE"]:
        template_form_pages = {reverse('people_update', args=[project_short_name, tab]): 'People'}
    else:
        template_form_pages = {reverse('aboutus_update', args=[project_short_name, tab]): 'About Us'}

    template_title = TAB_LABELS[tab]
    return templated_page_display(request, project_short_name, tab, template_page, template_title, template_form_pages)


@login_required
def aboutus_update(request, project_short_name, tab):
    """
    View to update the project "About Us" metadata.
    :param request:
    :param project_short_name:
    :param tab:
    :return:
    """

    # retrieve Project from database with the given short_name
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    # GET request
    if request.method == 'GET':
        # create form object from model
        form = AboutusForm(instance=project)

        return render_aboutus_form(request, project, tab, form)

    # POST request
    else:
        # update existing database model with form data
        form = AboutusForm(request.POST, instance=project)

        if form.is_valid():
            # save project data
            project = form.save()

            # redirect to about us display (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('aboutus_display', args=[project.short_name.lower(), tab]))

        else:
            # re-display form view
            if not form.is_valid():
                log.debug('Form is invalid  %s' % form.errors)
            return render_aboutus_form(request, project, tab, form)


def render_aboutus_form(request, project, tab, form):
    return render(request,
                  'cog/project/aboutus_form.html',
                   {'form': form, 'tab': tab,
                    'title': 'Update %s %s' % (project.short_name, TAB_LABELS[tab]),
                    'project': project})


@login_required
def impacts_update(request, project_short_name, tab):

    # load user from session, project from HTTP request
    user = request.user
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # check permission
    if not userHasContributorPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    # number of empty instances to be displayed
    # exclude fields 'project', so it doesn't get validated
    # allow for instances to be deleted
    nextras = 2
    ProjectImpactFormSet = modelformset_factory(ProjectImpact, extra=nextras, exclude=('project',), can_delete=True,
                                                formfield_callback=custom_field_callback)
    queryset = ProjectImpact.objects.filter(project=project)

    # GET
    if request.method == 'GET':

        # create formset instance backed by current saved instances
        # must provide the initial data to all the extra instances,
        # which come in the list after the database instances
        #queryset = ExternalUrl.objects.filter(project=project, type=type)
        #initial_data = [ {'project':project, 'type':type } for count in xrange(len(queryset)+nextras)]
        #formset = ExternalUrlFormSet(queryset=queryset,initial=initial_data)
        formset = ProjectImpactFormSet(queryset=queryset)

        return render_impacts_form(request, project, formset, tab)

    # POST
    else:

        formset = ProjectImpactFormSet(request.POST)

        if formset.is_valid():
            # select instances that have changed, don't save to database yet
            instances = formset.save(commit=False)
            for instance in instances:
                instance.project = project
                instance.order = 1
                instance.save()

            for obj in formset.deleted_objects:
                obj.delete()

            redirect = reverse('aboutus_display', args=[project_short_name, tab])
            return HttpResponseRedirect(redirect)

        else:
            log.debug(formset.errors)
            return render_impacts_form(request, project, formset, tab)


def render_impacts_form(request, project, formset, tab):
    return render(request,
                  'cog/project/aboutus_form.html',
                  {'formset': formset, 'tab': tab,
                   'title': 'Update %s %s' % (project.short_name, TAB_LABELS[tab]),
                   'project': project})


# function to customize the widget used by specific formset fields
def custom_field_callback(field):
    if field.name == 'description':
        return field.formfield(widget=Textarea(attrs={'rows': 4}))
    else:
        return field.formfield()


@login_required
def people_update(request, project_short_name, tab):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # Collaborator specific parameters
    clazz = Collaborator
    # explicit reference "CollaboratorForm to form to use custom text widgets
    formset_factory = modelformset_factory(Collaborator,
                                           form=CollaboratorForm,
                                           extra=5, can_delete=True, exclude=('project',))
    queryset = Collaborator.objects.filter(project=project).order_by('last_name')

    form_template = 'cog/project/people_form.html'
    upload_dir = UPLOAD_DIR_PHOTOS
    thumbnail_size = THUMBNAIL_SIZE_SMALL

    return _imageformset_update(request, project, tab,
                                clazz, formset_factory, queryset, form_template, upload_dir, thumbnail_size)


@login_required
def sponsors_update(request, project_short_name, tab):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # FundingSource specific parameters
    clazz = FundingSource
    # explicit reference to form FundingSourceForm to use custom text widgets
    formset_factory = modelformset_factory(FundingSource,
                                           form=FundingSourceForm,
                                           extra=3, can_delete=True, exclude=('project',))
    queryset = FundingSource.objects.filter(project=project).order_by('name')
    form_template = 'cog/project/sponsors_form.html'
    upload_dir = UPLOAD_DIR_LOGOS
    thumbnail_size = THUMBNAIL_SIZE_BIG

    return _imageformset_update(request, project, tab,
                                clazz, formset_factory, queryset, form_template, upload_dir, thumbnail_size)


@login_required
def partners_update(request, project_short_name, tab):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    # Organization specific parameters
    clazz = Organization
    formset_factory = modelformset_factory(Organization,
                                           # explicit reference to form to use custom text widgets
                                           form=OrganizationForm,
                                           extra=3, can_delete=True, exclude=('project',))
    queryset = Organization.objects.filter(project=project).order_by('name')

    form_template = 'cog/project/partners_form.html'
    upload_dir = UPLOAD_DIR_LOGOS
    thumbnail_size = THUMBNAIL_SIZE_BIG

    return _imageformset_update(request, project, tab,
                                clazz, formset_factory, queryset, form_template, upload_dir, thumbnail_size)


# generic view to update many objects (formsets) containing an image
def _imageformset_update(request, project, tab,
                         clazz, formset_factory, queryset, form_template, upload_dir, thumbnail_size):

    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    # GET request
    if request.method == 'GET':

        # select object instances associated with current project
        formset = formset_factory(queryset=queryset)

        return render_formset(form_template, request, project, tab, formset)

    # POST request
    else:
        # create formset from POST data
        formset = formset_factory(request.POST, request.FILES, queryset=queryset)

        # validate formset
        if formset.is_valid():

            # delete image?
            for form in formset:
                try:
                    # request to delete image or whole object
                    if form.cleaned_data.get('delete_image', False) or form.cleaned_data.get('DELETE', False):
                            deleteImageAndThumbnail(form.instance)

                except ValueError as error:
                    log.error(str(error))
                    
                # delete object
                if form.cleaned_data.get('DELETE', False):
                    log.debug('Deleting instance=%s' % form.instance)
                    form.instance.delete()

            # persist formset data
            # Note: only objects that have changed are returned
            instances = formset.save(commit=False)

            # assign instance to project and persist
            for instance in instances:

                # replace current image BEFORE the new image is persisted to disk
                # newly uploaded images are characterized by the fact that 'upload_dir' is not present in the path
                if (instance.id is not None                      # instance is not new (i.e. it's already in database)
                    and instance.image is not None               # instance contains an image
                    and instance.image.name is not None
                    and not upload_dir in instance.image.name):  # image has been newly selected
                    obj = clazz.objects.get(pk=instance.id)
                    try:
                        deleteImageAndThumbnail(obj)
                    except ValueError as error:
                        pass  # "The 'image' attribute has no file associated with it"

                instance.project = project
                instance.save()

                # generate image thumbnail, after the image has been saved to disk
                if instance.image is not None:
                    try:
                        generateThumbnail(instance.image.path, thumbnail_size)
                    except ValueError as e:
                        log.error(str(e))
                        pass  # no image supplied

            # redirect to people display (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('aboutus_display', args=[project.short_name.lower(), tab]))

        else:
            log.debug('Formset is invalid  %s' % formset.errors)
            return render_formset(form_template, request, project, tab, formset)


def render_formset(template, request, project, tab, formset):

    return render(request, template,
                  {'formset': formset, 'tab':tab,
                   'title': 'Update %s %s' % (project.short_name, TAB_LABELS[tab]),
                   'project': project })