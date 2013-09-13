from django.forms import ModelForm, BooleanField, Textarea, FileInput, TextInput, CharField
from cog.models import *
from cog.forms.forms_image import ImageForm
from cog.models.constants import RESEARCH_KEYWORDS_MAX_CHARS
from django.forms.models import BaseModelFormSet

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
        
# Custom form to define custom widget, and use 'delete_image' field        
class OrganizationForm(ImageForm):
    
    class Meta:
        model = Organization
        widgets = {
            'name' : TextInput(attrs={'size':30}),
            'url' : TextInput(attrs={'size':30}),
            'image': FileInput(),
        }
        
# Custom form to define custom widget, and use 'delete_image' field
class FundingSourceForm(ImageForm):
    
    class Meta:
        model = FundingSource
        widgets = {
            'name' : TextInput(attrs={'size':30}),
            'url' : TextInput(attrs={'size':30}),
            'image': FileInput(),
        }

# Custom form to define custom widget, and use 'delete_image' field
class CollaboratorForm(ImageForm):
             
    class Meta:
        model = Collaborator
        widgets = {
            'first_name' : TextInput(attrs={'size':20}),
            'last_name' : TextInput(attrs={'size':20}),
            'institution' : TextInput(attrs={'size':15}),
            'researchKeywords' : TextInput(attrs={'size':20}),
            'image': FileInput(),
            }
        
class ProjectImpactFormSet(BaseModelFormSet):
    
    def __init__(self, *args, **kwargs):
        super(ProjectImpactFormSet, self).__init__(*args, **kwargs)
    
    
