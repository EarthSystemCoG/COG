from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from models import *

urlpatterns = patterns('',
           
    # contact form
    url(r'^$', 'workspace.contact.views.contact_form', name='contact_form_url'),
    url(r'^thanks/$', TemplateView.as_view(template_name='contact/thanks.html'), name='contact_thanks'),
        
)

