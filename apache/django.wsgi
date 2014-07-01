import sys, os
sys.path.insert(0, '/usr/COG')

# note: settings.py is located under '/usr/COG/settings.py'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.conf import settings

import django.core.management
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
