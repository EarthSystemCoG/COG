# Django contect processor to add COG-specific settings to the request context,
# and make them available inside the template files.
from django.conf import settings # import the settings file

def cog_settings(request):
    
    # example key-value pair
    return {'DEFAULT_SEARCH_URL': settings.DEFAULT_SEARCH_URL }