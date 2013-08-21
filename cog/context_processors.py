# Django contect processor to add COG-specific settings to the request context,
# and make them available inside the template files
from django.conf import settings # import the settings file

def cog_settings(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'FACEBOOK_APPLICATION_ID': settings.FACEBOOK_APPLICATION_ID }