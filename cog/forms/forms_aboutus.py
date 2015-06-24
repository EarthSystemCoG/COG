from django.forms import ModelForm, BooleanField, Textarea, FileInput, TextInput, CharField
from cog.models import *
from cog.forms.forms_image import ImageForm
from cog.models.constants import RESEARCH_KEYWORDS_MAX_CHARS
from django.forms.models import BaseModelFormSet
from cog.forms.forms_utils import validate_image

class AboutusForm(ModelForm):
    
    class Meta:
        model = Project
        
                
        fields = ('long_name', 'description', 'external_homepage', # ABOUTUS
                  'mission', # MISSION
                  'vision',  # VISION
                  'values',  # VALUES
                  'history', # HISTORY
                  'projectContacts', 'technicalSupport', 'meetingSupport', 'getInvolved', # CONTACTUS   
                  'site',
                  )
        
        #exclude = ('short_name','parent','peers','author','active','private','logo','logo_url', 'maxUploadSize',
        #           'getting_started', 
        #           'software_features', 'system_requirements', 'license', 'implementationLanguage', 'bindingLanguage', 'supportedPlatforms', 'externalDependencies',
        #           'topics', 'tags', 'dataSearchEnabled',
        #           'taskPrioritizationStrategy','requirementsIdentificationProcess', 'developmentOverview', 'governanceOverview',)
                    
        widgets = {
                   'description': Textarea(attrs={'rows':6}),
                   'mission':     Textarea(attrs={'rows':8}),
                   'vision':      Textarea(attrs={'rows':8}),
                   'values':      Textarea(attrs={'rows':8}),
                   'history':     Textarea(attrs={'rows':12}),
                   }
        
# Custom form to define custom widget, and use 'delete_image' field        
class OrganizationForm(ImageForm):
    
    class Meta:
        model = Organization
        fields = "__all__" 
        widgets = {
            'name' : TextInput(attrs={'size':30}),
            'url' : TextInput(attrs={'size':30}),
            'image': FileInput(),
        }
        
# Custom form to define custom widget, and use 'delete_image' field
class FundingSourceForm(ImageForm):
    
    class Meta:
        model = FundingSource
        fields = "__all__" 
        widgets = {
            'name' : TextInput(attrs={'size':30}),
            'url' : TextInput(attrs={'size':30}),
            'image': FileInput(),
        }

# Custom form to define custom widget, and use 'delete_image' field
class CollaboratorForm(ImageForm):
             
    class Meta:
        model = Collaborator
        fields = "__all__" 
        widgets = {
            'first_name' : TextInput(attrs={'size':20}),
            'last_name' : TextInput(attrs={'size':20}),
            'institution' : TextInput(attrs={'size':15}),
            'researchKeywords' : TextInput(attrs={'size':20}),
            'image': FileInput(),
            }
        

    # override form clean() method to execute image validation
    def clean(self):

        # invoke superclass cleaning method
        super(CollaboratorForm, self).clean()
        
        # additional validation on 'image' field
        validate_image(self, 'image')

        return self.cleaned_data