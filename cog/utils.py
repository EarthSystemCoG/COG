import re
from django import forms

# list of invalid characters in text fields
#INVALID_CHARS = "[^a-zA-Z0-9\.\s\?\&\=_\-\:\/\#,]"
INVALID_CHARS = "[!@#$%^&*\[\]/{}|\"<>\\\]"
# shorter list specific to URL since the following characters are allowed for URLs: /#&
URL_INVALID_CHARS = "[!@$%^*\[\]\'{}|\"<>\\\]"

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
        
