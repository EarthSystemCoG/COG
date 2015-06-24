from cog.models import *
from django.forms import ModelForm, ModelMultipleChoiceField, NullBooleanSelect
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select, CheckboxSelectMultiple
from django.core.exceptions import ObjectDoesNotExist
from os.path import basename
import re
from cog.utils import *
from django.db.models import Q
import operator
from cog.forms.forms_utils import validate_image

# list of invalid characters in uploaded documents filenames
INVALID_CHARS = "[^a-zA-Z0-9_\-\.\/\s]"

class NewsForm(ModelForm):

    # extra fields not present in model
    peer_projects = ModelMultipleChoiceField(queryset=Project.objects.all(), required=False, widget=CheckboxSelectMultiple)
    parent_projects = ModelMultipleChoiceField(queryset=Project.objects.all(), required=False, widget=CheckboxSelectMultiple)
    child_projects = ModelMultipleChoiceField(queryset=Project.objects.all(), required=False, widget=CheckboxSelectMultiple)

    # override __init__ method to customize the list of choices for the parent/peer/child projects
    def __init__(self, project, user, *args, **kwargs):

        super(NewsForm, self).__init__(*args,**kwargs)

        self.fields['parent_projects'].queryset = Project.objects.filter(self._buildQuerySet(project.parents.all(), user)).distinct().order_by('short_name')
        self.fields['peer_projects'].queryset = Project.objects.filter(self._buildQuerySet(project.peers.all(), user)).distinct().order_by('short_name')
        self.fields['child_projects'].queryset = Project.objects.filter(self._buildQuerySet(project.children(), user)).distinct().order_by('short_name')

        # on update only: pre-populate extra fields with current selection
        if self.instance.id:
            self.fields['parent_projects'].initial=self.instance.other_projects.all()
            self.fields['peer_projects'].initial=self.instance.other_projects.all()
            self.fields['child_projects'].initial=self.instance.other_projects.all()

    # method to build a query set that contains only the projects the user has access to
    def _buildQuerySet(self, projects, user):
        qs = Q(pk=0) # start wuth an empty query set - does not match any project
        for p in projects:
            if userHasUserPermission(user, p):
                qs = qs | Q(pk=p.id)
        return qs

    class Meta:
        model = News

class DocForm(ModelForm):

    # extra field not present in model,
    # used for redirection to other URLs after for has been successfully submitted
    redirect = forms.CharField(required=False)
    
    # additional extra field to optionally create a resource under the selected folder
    folder = forms.ModelChoiceField(queryset=None, required=False)
    
    # override __init__ method to provide a filtered list of options for the bookmark folder
    def __init__(self, project, *args, **kwargs):
        
        super(DocForm, self).__init__(*args, **kwargs)
        
        # filter folders by project and active state
        # order by name in the form pull down
        self.fields['folder'].queryset = Folder.objects.filter(project=project).filter(active=True).distinct().order_by('name')

    def clean(self):
        ''' Override clean method to check that file size does not exceed limit.
            At this point the file is still in memory only,
            so if error is thrown there is no need to remove it from disk.'''
        cleaned_data = self.cleaned_data
        file = cleaned_data.get("file")
        
        if not file:
            self._errors["file"] = self.error_class(["Sorry, the file is empty."])
            return cleaned_data

        if re.search(INVALID_CHARS, file.name):
            self._errors['file'] = self.error_class(["Sorry, the filename contains invalid characters.  It can only contain letters, numbers, spaces, and _ - . /"])

        project = cleaned_data['project']
        if file.size > project.maxUploadSize:
            self._errors["file"] = self.error_class(["Sorry, the file size exceeds the maximum allowed."])

        return cleaned_data

    class Meta:
        model = Doc
        exclude = ('author','publication_date','update_date',)

class UploadImageForm(forms.Form):
    # note: field MUST be named 'upload' as this is the parameter named used by CKeditor
    upload  = forms.ImageField()

    # override 'clean' method to validate the image field
    def clean(self):
        
        # invoke superclass cleaning method
        super(UploadImageForm, self).clean()
        
        # validate image
        validate_image(self, 'upload')
                
        return self.cleaned_data
