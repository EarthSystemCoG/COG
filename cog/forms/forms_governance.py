from cog.models import *
from cog.utils import *
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.forms import ModelForm, ModelMultipleChoiceField, NullBooleanSelect, \
    ModelForm, Textarea, TextInput, Select, BooleanField, FileInput
from os.path import basename
import re
from django.db.models import Q
from cog.models.constants import MANAGEMENT_BODY_CATEGORY_STRATEGIC, MANAGEMENT_BODY_CATEGORY_OPERATIONAL
from os.path import exists
from cog.forms.forms_image import ImageForm
from cog.models.auth import getUserGroupName, getContributorGroupName, getAdminGroupName
import itertools


class ExternalUrlForm(ModelForm):

    class Meta:
        model = ExternalUrl
        fields = "__all__" 

class ManagementBodyForm(ModelForm):

    class Meta:
        model = ManagementBody
        exclude = ('category',)
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            'other': Textarea(attrs={'rows': 2}),
            'termsOfReference': Textarea(attrs={'rows': 8})
        }


class StrategicManagementBodyForm(ManagementBodyForm):
    """
    Subclass of ManagementBodyForm that limits the user choices for 'purposes' to the ManagementBodyPurpose of
    category='Strategic'.
    """

    def __init__(self, *args, **kwargs):

        super(StrategicManagementBodyForm, self).__init__(*args, **kwargs)

        # filter purposes by category
        self.fields['purposes'].queryset = ManagementBodyPurpose.objects.filter(
            category=MANAGEMENT_BODY_CATEGORY_STRATEGIC).order_by('order')


class OperationalManagementBodyForm(ManagementBodyForm):
    """
    Subclass of ManagementBodyForm that limits the user choices for 'purposes' to the ManagementBodyPurpose of
    category='Operational'.
    """

    def __init__(self, *args, **kwargs):

        super(OperationalManagementBodyForm, self).__init__(*args, **kwargs)

        # filter purposes by category
        self.fields['purposes'].queryset = ManagementBodyPurpose.objects.filter(
            category=MANAGEMENT_BODY_CATEGORY_OPERATIONAL).order_by('order')


class CommunicationMeansForm(ModelForm):

    class Meta:
        model = CommunicationMeans
        fields = "__all__" 

        widgets = {'frequency': Textarea(attrs={'rows': 1}),
                   'participationDetails': Textarea(attrs={'rows': 8}), }
        #widgets = { 'membership' : NullBooleanSelect() }


class GovernanceProcessesForm(ModelForm):

    class Meta:
        model = Project
        fields = ('taskPrioritizationStrategy', 'requirementsIdentificationProcess')
        widgets = {'taskPrioritizationStrategy': Textarea(attrs={'rows': 8}),
                   'requirementsIdentificationProcess': Textarea(attrs={'rows': 8}), }


class GovernanceOverviewForm(ModelForm):

    class Meta:
        model = Project
        widgets = {'governanceOverview': Textarea(attrs={'rows': 12}), }
        fields = ('governanceOverview', )


class OrganizationalRoleForm(ModelForm):

    class Meta:
        model = OrganizationalRole
        exclude = ('category',)
        widgets = {'description': Textarea(attrs={'rows': 4})}


class CommunicationMeansMemberForm(ModelForm):

    class Meta:
        model = CommunicationMeansMember
        fields = "__all__" 

    # override __init__ method to filter users by project
    def __init__(self, *args, **kwargs):
        super(CommunicationMeansMemberForm, self).__init__(*args, **kwargs)



class ManagementBodyMemberForm(ModelForm):

    class Meta:
        model = ManagementBodyMember
        fields = "__all__" 

    def __init__(self, *args, **kwargs):
        super(ManagementBodyMemberForm, self).__init__(*args, **kwargs)


class OrganizationalRoleMemberForm(ModelForm):

    class Meta:
        model = OrganizationalRoleMember
        fields = "__all__" 

    def __init__(self, *args, **kwargs):
        super(OrganizationalRoleMemberForm, self).__init__(*args, **kwargs)


# function to build a queryset that selects users of the given project
def projectUsersQuerySet(project):
        uGroup = getUserGroupName(project)
        cGroup = getContributorGroupName(project)
        aGroup = getAdminGroupName(project)
        query = Q(groups__name=uGroup) | Q(groups__name=cGroup) | Q(groups__name=aGroup)
        return User.objects.filter(query).distinct().order_by('username')
