from django.forms import Form, ModelForm, CharField
from cog.models import *
import re
from django import forms
from cog.utils import default_clean_field, clean_url_field

class SearchProfileForm(ModelForm):
    
    class Meta:
        model = SearchProfile
        
    def clean_url(self):
        return clean_url_field(self, 'url')
    
    def clean_constraints(self):
        return default_clean_field(self, 'constraints')
        
class SearchFacetForm(ModelForm):
    
    class Meta:
        model = SearchFacet
    
    # execute combined validation on form id and key
    # for each project, the search facet key must be unique
    def clean(self):
        
        cleaned_data = self.cleaned_data
        key = cleaned_data.get("key", None)
        label = cleaned_data.get("label", None)
        profile = cleaned_data.get("profile", None)
        
        # check key is unique        
        facets = SearchFacet.objects.filter(key=key).filter(profile__id=profile.id)
        for facet in facets:
            if self.instance is None or facet.id != self.instance.id:
                self._errors["key"] = self.error_class(["Facet with this key already exists in project"])
                if cleaned_data.get("key",None):
                    del cleaned_data["key"]
                
        # check label is unique
        facets = SearchFacet.objects.filter(label=label).filter(profile__id=profile.id)
        for facet in facets:
            if self.instance is None or facet.id != self.instance.id:
                self._errors["label"] = self.error_class(["Facet with this label already exists in project"])
                if cleaned_data.get("label",None):
                    del cleaned_data["label"]
        
        return cleaned_data
        
    def clean_key(self):
        return default_clean_field(self, 'key')
    
    def clean_label(self):
        return default_clean_field(self, 'label')
