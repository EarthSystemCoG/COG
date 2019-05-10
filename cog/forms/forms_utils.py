'''
General utilities for form validation

@author: Luca Cinquini
'''

import imghdr
import logging
import os

log = logging.getLogger(__name__)

def validate_image(form, field_name):
    '''
    Validates an image field that is part of a form,
    before the image is uploaded to the server.
    '''
    
    cleaned_data = form.cleaned_data
    image = cleaned_data.get(field_name, None)
    if image is not None:
            
        # enforce white-list of allowed extensions
        extension = (os.path.splitext(image.name)[1]).lower()
        if (extension != '.jpg' and extension != '.png' and extension != '.gif' and extension != '.jpeg'
            and extension != '.tif' and extension != '.tiff'):
            form._errors[field_name] = form.error_class(["Invalid image format: %s"%extension])
        
        # validate image header
        try:
            image_type = imghdr.what(image)
            log.debug('Validating image header: detected image type=%s' % image_type)
            if image_type is None:
                form._errors[field_name] = form.error_class(["Invalid image type: %s" % image_type])
        except Exception as e:
            form._errors[field_name] = form.error_class(["Cannot validate image header: %s" % e.message])
