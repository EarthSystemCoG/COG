from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
import django.views.static, django.views.generic
import cog.views
from django.http.response import HttpResponseNotFound

from filebrowser.sites import site

admin.autodiscover()

urlpatterns = [
                       
    # forbidden extensions (case-insensitive)
    url(r'.*\.asp\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.aspx\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.cfm\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.cgi\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.jsp\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.php\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.php3\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.pl\/?$(?i)', HttpResponseNotFound),
    url(r'.*\.shtml\/?$(?i)', HttpResponseNotFound),
    
    url(r'^robots\.txt$', django.views.generic.TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots.txt'),
                                                      
    # site index
    url(r'^$', cog.views.site_home, name='site_home'),
                           
    # Grappelli
    url(r'^grappelli/', include('grappelli.urls')),
    
    # Filebrowser Admin pages
    #(r'^filebrowser/', include('filebrowser.urls')),
    url(r'^admin/filebrowser/', site.urls),

    # Administrator application
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
            
    # django-simple-captcha
    url(r'^captcha/', include('captcha.urls')),
    
    # OpenID URLs included within CoG URLs
    #(r'^openid/', include('django_openid_auth.urls')),
            
    # COG application
    url(r'', include('cog.urls')),
    
    # other media (when NOT served through the Apache web server)
    # Note: the media must be located under <application>/static/<application>, not static/<application>
    url(r'^static/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT} ),
    url(r'^site_media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT} ),
    url(r'^static_media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT} ),    
    url(r'^mymedia/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MYMEDIA } ),

]
