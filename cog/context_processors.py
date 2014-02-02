# Django contect processor to add COG-specific settings to the request context,
# and make them available inside the template files.

from django.conf import settings # import the settings file
from django.contrib.sites.models import Site

def cog_settings(request):
    
    # example key-value pair
    return { 'site': Site.objects.get_current(),
            'DEFAULT_SEARCH_URL': settings.DEFAULT_SEARCH_URL }