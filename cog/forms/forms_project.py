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
from cog.forms.forms_image import ImageForm


class ProjectForm(ModelForm):
    
    # note: alternative widget for peer selection would require additional js and css
    #peers = ModelMultipleChoiceField(Project.objects.all(),
    #        widget=FilteredSelectMultiple("Peer Projects", False, attrs={'rows':'10'}))
    
    # extra field not present in model, used for deletion of previously uploaded logo
    delete_logo = forms.BooleanField(required=False)
    # specify size of logo_url text field
    logo_url = forms.CharField(required=False, widget=TextInput(attrs={'size':'80'}))
    
    # override __init__ method to change the querysets for 'parent' and 'peers'
    def __init__(self, *args, **kwargs):
        
        super(ProjectForm, self ).__init__(*args,**kwargs) # populates the post
         
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            # parent query-set options: exclude the project itself, and all its children  
            parentQueryset =  ~Q(id=instance.id)
            # FIXME ? Should children be excluded from list of possible parents ?
            # exclude children from parents
            #for child in instance.children():
            #    parentQueryset = parentQueryset & ~Q(id=child.id)
            # make the ordering case=independent (NOTE: the generated SQL is database-dependent!)
            #self.fields['parents'].queryset =  Project.objects.filter( parentQueryset ).distinct().order_by('short_name')
            self.fields['parents'].queryset =  Project.objects.filter( parentQueryset ).distinct().extra( select={'snl':'lower(short_name)'}, order_by = ['snl'] )
            # peer query-set options: exclude the project itself
            #self.fields['peers'].queryset =  Project.objects.filter( ~Q(id=instance.id) ).distinct().order_by('short_name')
            self.fields['peers'].queryset =  Project.objects.filter( ~Q(id=instance.id) ).distinct().extra( select={'snl':'lower(short_name)'}, order_by = ['snl'] )

    
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
        exclude = ('topics','mission','values','vision','history','taskPrioritizationStrategy','requirementsIdentificationProcess','governanceOverview',
                   'developmentOverview',
                   'software_features', 'software_system_requirements', 'software_supported_platforms',
                   'getting_started')
        
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
                   'license': Textarea(attrs={'rows':4}),
                   'implementationLanguage': TextInput(),
                   'bindingLanguage': TextInput(),
                   'supportedPlatforms': Textarea(attrs={'rows':4}),
                   'externalDependencies': Textarea(attrs={'rows':4}), }                                     
        fields = ( 'developmentOverview', 'license', 'implementationLanguage', 'bindingLanguage', 
                   'supportedPlatforms', 'externalDependencies')
        
class SoftwareForm(ModelForm):
    
    class Meta:
        model = Project        
        widgets = {'software_features': Textarea(attrs={'rows':6}),
                   'software_system_requirements': Textarea(attrs={'rows':4}),
                   'software_supported_platforms': Textarea(attrs={'rows':4}),
                   }
        fields = ( 'software_features', 'software_system_requirements', 'software_supported_platforms')
        
class UsersForm(ModelForm):
    
    class Meta:
        model = Project        
        widgets = { 'getting_started': Textarea(attrs={'rows':10}), }
        fields = ( 'getting_started', )
        
class ProjectTagForm(ModelForm):
    
    # additional field to select existing tags
    tags = ModelMultipleChoiceField(queryset=ProjectTag.objects.all(), required=False)
     
    def clean(self):
        name = self.cleaned_data['name']
        
        try:
            tag = ProjectTag.objects.get(name__iexact=name)
            # check tag with same name (independently of case) does not exist already
            if tag is not None and tag.id != self.instance.id: # not this tag
                self._errors["name"] = self.error_class(["Tag with this name already exist: %s" % tag.name])
        except ObjectDoesNotExist :  
            # capitalize the tag name
            self.cleaned_data['name'] = self.cleaned_data['name'].capitalize()
            # only allow letters, numbers, '-' and '_'
            if re.search("[^a-zA-Z0-9_\-\s]", name):
                self._errors["name"] = self.error_class(["Tag name contains invalid characters"])
            # impose maximum length
            if len(name)>MAX_PROJECT_TAG_LENGTH:
                self._errors["name"] = self.error_class(["Tag name must contain at most %s characters" % MAX_PROJECT_TAG_LENGTH])
        
        return self.cleaned_data
    
    class Meta:
        model = ProjectTag    