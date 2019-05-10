from django.forms import ModelForm, BooleanField
import os
import logging

MAX_IMAGE_SIZE = 1048576 # 1MB

log = logging.getLogger(__name__)

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
        try:
            if image is not None and delete_image is False and image.size > MAX_IMAGE_SIZE:
                self._errors["image"] = self.error_class(["Image size exceeds the maximum allowed."])
        except OSError as e:
            # image not existing on disk
            log.error(str(e))
        
        return self.cleaned_data