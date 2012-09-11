from cog.models import *
from django.forms import ModelForm, ModelMultipleChoiceField, NullBooleanSelect
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE
from os.path import basename
import re
from cog.utils import *
from django.db.models import Q


class NewsForm(ModelForm):
    class Meta:
        model = News
        
class DocForm(ModelForm):
    
    # extra field not present in model, 
    # used for redirection to other URLs after for has been successfully submitted
    redirect = forms.CharField(required=False)
    
    class Meta:
        model = Doc
        exclude = ('author','publication_date','update_date')
        
class UploadImageForm(forms.Form):
    # note: field MUST be named 'upload' as this is the parameter named used by CKeditor
    upload  = forms.ImageField()