import sys, os
sys.path.insert(0, '/usr/COG')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cog.settings")
from django.conf import settings

#import django.core.management
#django.core.management.setup_environ(settings)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

# needed for HTTPS support 
# (instructs Django to prepend 'https' to fully generated links)
os.environ['HTTPS'] = "on"
