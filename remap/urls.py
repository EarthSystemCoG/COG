from django.conf.urls.defaults import *
from models import *

urlpatterns = patterns('',
    
    # remap input form
    url(r'^$', 'remap.views.remap_form', name='remap_form' ),
    
    # remap RESTful web service
    url(r'^srcgrid=(?P<srcgrid>.+)/dstgrid=(?P<dstgrid>.+)/method=(?P<method>.+)/(?P<weights>.+)$', 'remap.views.remap_job', name='remap_job' ),
    
)