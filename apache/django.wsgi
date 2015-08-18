import sys, os
sys.path.insert(0, '/usr/local/cog/cog_install')

# print debugging information BEFORE import Django/CoG
print 'Using Python version: %s' % sys.version
print 'Using Python path: %s' % sys.path
print 'PYTHONPATH=%s' % os.environ.get('PYTHONPATH', None)
print 'LD_LIBRARY_PATH=%s' % os.environ.get('LD_LIBRARY_PATH', None)
print 'SSL_CERT_DIR=%s' % os.environ.get('SSL_CERT_DIR', None)

# note: settings.py is located under '/usr/local/cog/cog_install/settings.py'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.conf import settings

from django import setup as django_setup
django_setup()

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
