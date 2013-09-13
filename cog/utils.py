import re
from django import forms

# list of invalid characters in text fields
#INVALID_CHARS = "[^a-zA-Z0-9\.\s\?\&\=_\-\:\/\#,]"
INVALID_CHARS = "[!@#$%^&*\[\]/{}|\"<>\\\]"
# shorter list specific to URL since the following characters are allowed for URLs: /#&
URL_INVALID_CHARS = "[!@$%^*\[\]\'{}|\"<>\\\]"

def hasText(str):
    '''Utility function to establish whether a string has any non-empty characters.'''
    return str is not None and len(str.strip()) > 0

# method to check a form field for invalid characters
def clean_field(form, field, invalid_characters):
    data = form.cleaned_data[field]
    #if re.search(INVALID_CHARS, data):
    #    raise forms.ValidationError("The field %s contains invalid characters" % field)
    for c in data:
        if re.match(invalid_characters, c):
            print 'Invalid character: %s' % c
            raise forms.ValidationError("The character '%s' is invalid" % c)
    return data

# method to clean a URL field
def clean_url_field(form, field):
    return clean_field(form, field, URL_INVALID_CHARS)

# method to check a field for the default bad characters
def default_clean_field(form, field):
    return clean_field(form, field, INVALID_CHARS)

# Function to truncate a string at some word limit
def smart_truncate(s, width):
    if width >= len(s):
        return s
    else:
        if s[width].isspace():
            return s[0:width];
        else:
            return s[0:width].rsplit(None, 1)[0] +" ..."
        
def create_resized_image(newimagepath, imagepath, xconstrain=200, yconstrain=200):
    """
    Function to create a resized image from an original image location.
    """
    from PIL import Image, ImageOps
    import urllib
    import os
    from django.conf import settings
    
        # delete previous image
    if os.path.exists(newimagepath):
        os.remove(newimagepath)
    
    # create new image
    unsized_image = urllib.urlretrieve(str(imagepath)) # Fetch original image
    unsized_image = Image.open(unsized_image[0]) # Load the fetched image
    resized_image = ImageOps.fit(unsized_image, (xconstrain, yconstrain), Image.ANTIALIAS) # Create a resized image by fitting the original image into the constrains, and do this using proper antialiasing
    resized_image = resized_image.convert("RGB") # PIL sometimes throws errors if this isn't done
    resized_image.save(newimagepath) # Save the resized image as a jpeg into the MEDIA_ROOT/images/resized

    return newimagepath