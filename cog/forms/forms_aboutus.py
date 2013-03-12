from django.forms import ModelForm, BooleanField, Textarea, FileInput, TextInput
from cog.models import *

MAX_IMAGE_SIZE = 1048576 # 1MB

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

class ImageForm(ModelForm):
    '''Generic custom form for models containing an ImageField.'''
    
    # extra field not present in model, used for deletion of previously uploaded image
    delete_image = BooleanField(required=False)
    
    #  override form clean() method to execute custom validation on 'image' field.
    def clean(self):
                
        # invoke superclass cleaning method
        super(ImageForm, self).clean()
            
        # check image size on upload    
        image = self.cleaned_data.get("image")
        delete_image = self.cleaned_data.get("delete_image")
        if image is not None and delete_image is False and image.size > MAX_IMAGE_SIZE:
            self._errors["image"] = self.error_class(["Image size exceeds the maximum allowed."])
        
        return self.cleaned_data
        
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
