from django.forms import Form, ModelForm, CharField
from cog.models import *
import re
from django import forms
from cog.utils import default_clean_field, clean_url_field


class SearchProfileForm(ModelForm):
    
    class Meta:
        model = SearchProfile
        fields = "__all__" 

    def clean_url(self):
        return clean_url_field(self, 'url')
    
    def clean_constraints(self):
        return clean_url_field(self, 'constraints')


class SearchFacetForm(ModelForm):
    
    class Meta:
        model = SearchFacet
        fields = "__all__" 
        
    # override __init__ method to sub-select the available facet groups
    def __init__(self, project, *args, **kwargs):
        
        super(SearchFacetForm, self).__init__(*args, **kwargs)
        
        # filter search groups by project
        # order by name in the form pull down
        self.fields['group'].queryset = SearchGroup.objects.filter(profile__project=project).distinct().order_by('order')
                
        # remove the empty option
        self.fields['group'].empty_label = None

    
    # execute combined validation on form id and key
    # for each project, the search facet key and label must be unique
    def clean(self):
        
        cleaned_data = self.cleaned_data
        key = cleaned_data.get("key", None)
        label = cleaned_data.get("label", None)
        group = cleaned_data.get("group", None)
        
        # check key, label are unique among this project search profile   
        for facet in group.profile.facets():
            if self.instance is None or facet.id != self.instance.id:
                if facet.key == key:
                    self._errors["key"] = self.error_class(["Facet with this key already exists in project"])
                if facet.label == label:
                    self._errors["label"] = self.error_class(["Facet with this label already exists in project"])
                        
        return cleaned_data
        
    def clean_key(self):
        return default_clean_field(self, 'key')
    
    def clean_label(self):
        return default_clean_field(self, 'label')
    
class SearchGroupForm(ModelForm):
    
    class Meta:
        model = SearchGroup
        fields = "__all__" 

    def clean_name(self):
        return default_clean_field(self, 'name')

    def clean(self):
        
        cleaned_data = self.cleaned_data
        name = cleaned_data.get("name", None)
        profile = cleaned_data.get("profile", None)
        try:
            groups = SearchGroup.objects.filter(profile=profile)
            for group in groups:
                if name.lower() == group.name.lower():
                    self._errors["name"] = self.error_class(["Search Facet Group wit this name already exists in project"])
        except:
            pass
                                
        return cleaned_data