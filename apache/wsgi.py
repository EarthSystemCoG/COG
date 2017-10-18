"""
This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import time
import traceback
import signal
import sys
from django.core.wsgi import get_wsgi_application

sys.path.insert(0, '/usr/local/cog/cog_install')

os.environ["COG_CONFIG_DIR"] = "/usr/local/cog/cog_config"
os.environ['HTTPS'] = "on" # instructs Django to prepend 'https' to fully generated links
os.environ["SSL_CERT_DIR"] = "/etc/grid-security/certificates"
os.environ["SSL_CERT_FILE"] = "/etc/certs/esgf-ca-bundle.crt"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# print debugging information
print 'Using Python version: %s' % sys.version
print 'Using Python path: %s' % sys.path
print 'PYTHONPATH=%s' % os.environ.get('PYTHONPATH', None)
print 'LD_LIBRARY_PATH=%s' % os.environ.get('LD_LIBRARY_PATH', None)
print 'SSL_CERT_DIR=%s' % os.environ.get('SSL_CERT_DIR', None)
print 'SSL_CERT_FILE=%s' % os.environ.get('SSL_CERT_FILE', None)

try:
    application = get_wsgi_application()
    print 'WSGI without exception'
except Exception:
    print 'handling WSGI exception'
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
