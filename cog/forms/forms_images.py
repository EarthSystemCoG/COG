from django.forms import ModelForm, BooleanField

class ImageForm(ModelForm):
    '''Generic custom form for models containing an ImageField.'''
    
    # extra field not present in model, used for deletion of previously uploaded image
    delete_image = BooleanField(required=False)
