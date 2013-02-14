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
from cog.models.constants import MAX_UPLOADES_BYTES

# list of invalid characters in uploaded documents filenames
INVALID_CHARS = "[^a-zA-Z0-9_\-\.\/]"

class NewsForm(ModelForm):
    class Meta:
        model = News
        
class DocForm(ModelForm):
    
    # extra field not present in model, 
    # used for redirection to other URLs after for has been successfully submitted
    redirect = forms.CharField(required=False)
    
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
            self._errors['file'] = self.error_class(["Sorry, the filename contains invalid characters.  It can only contain letters, numbers, and one of _ - . /."])
        
        if file.size > MAX_UPLOADES_BYTES:
            self._errors["file"] = self.error_class(["Sorry, the file size exceeds the maximum allowed."])
            
        return cleaned_data
    
    class Meta:
        model = Doc
        exclude = ('author','publication_date','update_date')
        
class UploadImageForm(forms.Form):
    # note: field MUST be named 'upload' as this is the parameter named used by CKeditor
    upload  = forms.ImageField()
    
