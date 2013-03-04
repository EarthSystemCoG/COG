from cog.models import *
from django.forms import ModelForm, ModelMultipleChoiceField, NullBooleanSelect
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select, FileInput
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE
from os.path import basename
import re
from cog.utils import *
from django.db.models import Q
from cog.forms.forms_images import ImageForm


class ProjectForm(ModelForm):
    
    # note: alternative widget for peer selection would require additional js and css
    #peers = ModelMultipleChoiceField(Project.objects.all(),
    #        widget=FilteredSelectMultiple("Peer Projects", False, attrs={'rows':'10'}))
    
    # extra field not present in model, used for deletion of previously uploaded logo
    delete_logo = forms.BooleanField(required=False)
    # specify size of logo_url text field
    logo_url = forms.CharField(required=False, widget=TextInput(attrs={'size':'80'}))
    
    # override __init__ method to change the querysets for 'parent' and 'peers'
    def __init__(self,  *args,**kwargs):
        
        super(ProjectForm, self ).__init__(*args,**kwargs) # populates the post
         
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            # parent query-set options: exclude the project itself, and all its children  
            parentQueryset =  ~Q(id=instance.id)
            # exclude children from parent
            for child in instance.children():
                parentQueryset = parentQueryset & ~Q(id=child.id)
            self.fields['parent'].queryset =  Project.objects.filter( parentQueryset ).distinct().order_by('short_name')
            # peer query-set options: exclude the project itself
            self.fields['peers'].queryset =  Project.objects.filter( ~Q(id=instance.id) ).distinct().order_by('short_name')

    
    # overridden validation method for project short name 
    def clean_short_name(self):
        short_name = self.cleaned_data['short_name']
        # must not start with any of the URL matching patterns
        if short_name in ('admin', 'project', 'news', 'post', 'doc', 'signal'):
            raise forms.ValidationError("Sorry, '%s' is a reserved URL keyword - it cannot be used as project short name" % short_name)
        # only allows letters, numbers, '-' and '_'
        if re.search("[^a-zA-Z0-9_\-]", short_name):
            raise forms.ValidationError("Project short name contains invalid characters")
        return short_name
    
    class Meta:
        model = Project
        # Note: must exclude the many2many field mapped through an intermediary table
        exclude = ('topics','mission','values','vision','history','taskPrioritizationStrategy','requirementsIdentificationProcess','governanceOverview','developmentOverview')

    
class AboutusForm(ModelForm):
    
    class Meta:
        model = Project
        exclude = ('short_name','parent','peers','author','active','private','logo','logo_url',
                   'topics','taskPrioritizationStrategy','requirementsIdentificationProcess', 'developmentOverview', 'governanceOverview')
        widgets = {
                   'description': Textarea(attrs={'rows':6}),
                   'mission':     Textarea(attrs={'rows':6}),
                   'vision':      Textarea(attrs={'rows':6}),
                   'values':      Textarea(attrs={'rows':6}),
                   'history':     Textarea(attrs={'rows':6}),
                   }
        
class ContactusForm(ModelForm):
    
    class Meta:
        model = Project
        fields = ('long_name', 'description')
        widgets = { 'description': Textarea(attrs={'rows':6}), }
        
class SupportForm(ModelForm):
    
    class Meta:
        model = Project
        fields = ('long_name', 'mission')
        widgets = { 'mission': Textarea(attrs={'rows':6}), }
        
class GetInvolvedForm(ModelForm):
    
    class Meta:
        model = Project
        fields = ('long_name', 'mission')
        widgets = { 'mission': Textarea(attrs={'rows':6}), }
        
class DevelopmentOverviewForm(ModelForm):
    
    class Meta:
        model = Project        
        widgets = {'developmentOverview': Textarea(attrs={'rows':6}),
                   'license': TextInput(),
                   'implementationLanguage': TextInput(),
                   'bindingLanguage': TextInput(),
                   'supportedPlatforms': TextInput(),
                   'externalDependencies': Textarea(attrs={'rows':4}), }                                     
        fields = ( 'developmentOverview', 'license', 'implementationLanguage', 'bindingLanguage', 
                   'supportedPlatforms', 'externalDependencies')
        
class OrganizationForm(ImageForm):
    
    class Meta:
        model = Organization
        widgets = {
            'name' : forms.fields.TextInput(attrs={'size':30}),
            'url' : forms.fields.TextInput(attrs={'size':30}),
            'image': FileInput(),
        }
        
class FundingSourceForm(ImageForm):
    
    class Meta:
        model = FundingSource
        widgets = {
            'name' : forms.fields.TextInput(attrs={'size':30}),
            'url' : forms.fields.TextInput(attrs={'size':30}),
            'image': FileInput(),
        }
