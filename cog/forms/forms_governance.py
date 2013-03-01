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
from tinymce.widgets import TinyMCE
import re
from django.db.models import Q
from cog.models.constants import MANAGEMENT_BODY_CATEGORY_STRATEGIC, MANAGEMENT_BODY_CATEGORY_OPERATIONAL
from os.path import exists

        
class ExternalUrlForm(ModelForm):
    
    class Meta:
        model = ExternalUrl
        widgets = { 'url': TextInput(attrs={'size':'120'}),
                    'title': TextInput(attrs={'size':'120'}) }
                
class ManagementBodyForm(ModelForm):
    
    class Meta:
        model = ManagementBody
        exclude = ('category')
        widgets = {
                   'description': Textarea(attrs={'rows':4}),
                   'termsOfReference': Textarea(attrs={'rows':2})
                   }
        
class StrategicManagementBodyForm(ManagementBodyForm):
    """Subclass of ManagementBodyForm that limits the user choices for 'purposes' to the ManagementBodyPurpose of category='Strategic'."""
    
    def __init__(self, *args, **kwargs):
        
        super(StrategicManagementBodyForm, self ).__init__(*args,**kwargs)
        
        # filter purposes by category
        self.fields['purposes'].queryset = ManagementBodyPurpose.objects.filter(category=MANAGEMENT_BODY_CATEGORY_STRATEGIC).order_by('order')
        
class OperationalManagementBodyForm(ManagementBodyForm):
    """Subclass of ManagementBodyForm that limits the user choices for 'purposes' to the ManagementBodyPurpose of category='Operational'."""
    
    def __init__(self, *args, **kwargs):
        
        super(OperationalManagementBodyForm, self ).__init__(*args,**kwargs)
        
        # filter purposes by category
        self.fields['purposes'].queryset = ManagementBodyPurpose.objects.filter(category=MANAGEMENT_BODY_CATEGORY_OPERATIONAL).order_by('order')
        
    
    
class CommunicationMeansForm(ModelForm):
        
    class Meta:
        model = CommunicationMeans  
        widgets = { 'participationDetails': Textarea(attrs={'rows':4}), }      
        #widgets = { 'membership' : NullBooleanSelect() }
        
class GovernanceProcessesForm(ModelForm):
    
    class Meta:
        model = Project
        fields = ('taskPrioritizationStrategy','requirementsIdentificationProcess')
        widgets = { 'taskPrioritizationStrategy': Textarea(attrs={'rows':6}),
                    'requirementsIdentificationProcess': Textarea(attrs={'rows':6}), }
        
class GovernanceOverviewForm(ModelForm):
    
    class Meta:
        model = Project
        widgets = { 'governanceOverview': Textarea(attrs={'rows':10}), }
        fields = ( 'governanceOverview', )
        
class OrganizationalRoleForm(ModelForm):
    
    class Meta:
        model = OrganizationalRole
        exclude = ('category')
        widgets = { 'description': Textarea(attrs={'rows':2}) }
        
        
class CommunicationMeansMemberForm(ModelForm):
    
    class Meta:
        model = CommunicationMeansMember
    
    # override __init__ method to filter users by project
    def __init__(self, *args,**kwargs):
        
        project = kwargs.pop('project')
        super(CommunicationMeansMemberForm, self ).__init__(*args,**kwargs)
        
        # filter parent posts by project and type
        self.fields['user'].queryset = projectUsersQuerySet(project)
        
class ManagementBodyMemberForm(ModelForm):
    
    class Meta:
        model = ManagementBodyMember
    
    # override __init__ method to filter users by project
    def __init__(self, *args,**kwargs):
        
        project = kwargs.pop('project')
        super(ManagementBodyMemberForm, self ).__init__(*args,**kwargs)
        
        # filter parent posts by project and type
        self.fields['user'].queryset = projectUsersQuerySet(project)
        
class OrganizationalRoleMemberForm(ModelForm):
    
    class Meta:
        model = OrganizationalRoleMember
    
    # override __init__ method to filter users by project
    def __init__(self, *args,**kwargs):
        
        project = kwargs.pop('project')
        super(OrganizationalRoleMemberForm, self ).__init__(*args,**kwargs)
        
        # filter parent posts by project and type
        self.fields['user'].queryset = projectUsersQuerySet(project)

# function to build a queryset that selects users of the given project
def projectUsersQuerySet(project):
        uGroup = getUserGroupName(project)
        aGroup = getAdminGroupName(project)
        query = Q(groups__name=uGroup) | Q(groups__name=aGroup)
        return User.objects.filter(query).distinct().order_by('username')
    
# Use a custom form for the Collaborator formset to 
# a) explicitely define the widget properties
# b) use custom validation on the 'photo' field
# c) use the extra field 'delete_photo'
class CollaboratorForm(forms.ModelForm):
    
    # extra field not present in model, used for deletion of previously uploaded photo
    delete_photo = BooleanField(required=False)
    
    def clean(self):
        
        # invoke superclass cleaning method
        super(CollaboratorForm, self).clean()
        
        # do not override existing photos
        photo = self.cleaned_data.get("photo", None)
        if photo is not None:
            try:              
                # a) new collaborator, new photo
                if self.instance.id is None:                    
                    self._validate_photo(photo)             
                # b) existing collaborator     
                else:
                    collaborator = Collaborator.objects.get(pk=self.instance.id)
                    # b1) new photo
                    if photo.name not in collaborator.photo.name:
                        self._validate_photo(photo)
                    # b2) same photo, but without the 'photos/' path prepended
                    elif len(photo.name) != len(collaborator.photo.name):
                        self._errors['photo'] = self.error_class(['File %s already exists.' % photo.name]) 
                        
            except ValueError as error:
                print error
                
        return self.cleaned_data
    
    def _validate_photo(self, photo):
        
        filepath = settings.MEDIA_ROOT+'photos/'+photo.name
        if exists(filepath):
            self._errors['photo'] = self.error_class(['File %s already exists.' % photo.name])         
        
    class Meta:
        model = Collaborator
        widgets = {
            'first_name' : forms.fields.TextInput(attrs={'size':25}),
            'last_name' : forms.fields.TextInput(attrs={'size':25}),
            'institution' : forms.fields.TextInput(attrs={'size':25}),
            'photo': FileInput(),
            }