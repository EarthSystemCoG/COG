from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings


from filebrowser.sites import site

admin.autodiscover()

urlpatterns = patterns('',
                           
    # site index
    url(r'^$', 'cog.views.site_home', name='site_home'),
                           
    # Grappelli
    (r'^grappelli/', include('grappelli.urls')),
    
    # Filebrowser Admin pages
    #(r'^filebrowser/', include('filebrowser.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),

    # Administrator application
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
        
    # Comments
    (r'^comments/', include('django.contrib.comments.urls')),
    
    # OpenID URLs included within CoG URLs
    #(r'^openid/', include('django_openid_auth.urls')),
            
    # COG application
    (r'', include('cog.urls')),
    
    # other media (when NOT served through the Apache web server)
    # Note: the media must be located under <application>/static/<application>, not static/<application>
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT} ),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    url(r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT} ),    
    url(r'^mymedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MYMEDIA } ),


)
