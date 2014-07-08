# Python script to upgrade the content of an existing COG installation
import sys, os, ConfigParser
from django.core.exceptions import ObjectDoesNotExist

sys.path.append( os.path.abspath(os.path.dirname('.')) )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from cog.models import *

print 'Upgrading COG to version 2.2'

for user in User.objects.all():
    
    try:    
        dc = DataCart.objects.get(user=user)
    except ObjectDoesNotExist:
        print 'Creating data cart for user: %s' % user
        dc = DataCart(user=user)
        dc.save()
