import re
from django import forms
import os
import datetime
import urllib2
import json
import logging

log = logging.getLogger(__name__)
# timeout for JSON HTTP requests
TIMEOUT = 5

# list of invalid characters in text fields
#INVALID_CHARS = "[^a-zA-Z0-9\.\s\?\&\=_\-\:\/\#,]"
INVALID_CHARS = "[@#$%^&*\[\]/{}|\"<>\\\]"
# shorter list specific to URL since the following characters are allowed for URLs: /#&
URL_INVALID_CHARS = "[@$^*\[\]\'{}|\"<>\\\]"
# even shorter list of invdali charactes to prevent XSS
XSS_INVALID_CHARS = "[<>]"

def hasText(str):
    '''Utility function to establish whether a string has any non-empty characters.'''
    return str is not None and len(str.strip()) > 0

def str2bool(s):
    '''Utility methid to parse a string into a boolean.'''
    return s.lower() in ("yes", "true", "t", "1")

def file_modification_datetime(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

# method to check a form field for invalid characters
def clean_field(form, field, invalid_characters):
    data = form.cleaned_data[field]
    #if re.search(INVALID_CHARS, data):
    #    raise forms.ValidationError("The field %s contains invalid characters" % field)
    for c in data:
        if re.match(invalid_characters, c):
            log.error('Invalid character: %s' % c)
            raise forms.ValidationError("The character '%s' is invalid." % c)
    return data

# method to clean a URL field
def clean_url_field(form, field):
    return clean_field(form, field, URL_INVALID_CHARS)

# method to check a field for the default bad characters
def default_clean_field(form, field):
    return clean_field(form, field, INVALID_CHARS)

# method to check for the presence of XSS enabling characters
def xss_clean_field(form, field):
    return clean_field(form, field, XSS_INVALID_CHARS)

# Function to truncate a string at some word limit
def smart_truncate(s, width):
    if width >= len(s):
        return s
    else:
        if s[width].isspace():
            return s[0:width];
        else:
            return s[0:width].rsplit(None, 1)[0] +" ..."

def getJson(url):
    '''Retrieves and parses a JSON document at some URL.'''
    
    try:
        opener = urllib2.build_opener()
        request = urllib2.Request(url)
        response = opener.open(request, timeout=TIMEOUT)
        jdoc = response.read()
        return json.loads(jdoc)
        
    except Exception as e:
        log.error('Error retrieving URL=%s. Error: %s' % (url,  str(e)))
        return None
    
def check_filepath(file_full_path, expected_file_names):
    '''Method to check that a file full path matches the expected file name.
       This is useful to avoid possible path manipulation issues.
       If no problems are found, the original file path is returned. '''
    
    (head, tail) = os.path.split(file_full_path)
    if tail not in expected_file_names:
        raise Exception("Invalid file path to be read: %s" % file_full_path)
    
    # also check for directory recursiveness
    if '.' in head:
        raise Exception("Invalid file path to be read: %s" % file_full_path)
    
    return file_full_path
    