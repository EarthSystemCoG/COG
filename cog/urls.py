from django.conf.urls import patterns, url, include
from cog.models import *
from cog.views.views_account import custom_login, custom_login_complete

urlpatterns = patterns('',

    # indexes
    url(r'^$', 'cog.views.index', name='cog_index' ) ,
    url(r'^cogadmin/$', 'cog.views.admin_index', name='admin_index' ),

    # overridden search page to execute project-dependent configuration
    url(r'^search/(?P<project_short_name>.+)/$', 'cog.views.search', name='search' ),
    url(r'^search_profile/config/(?P<project_short_name>.+)/$', 'cog.views.search_profile_config', name='search_profile_config'),
    url(r'^search_facet/add/(?P<project_short_name>.+)/$', 'cog.views.search_facet_add', name='search_facet_add'),
    url(r'^search_facet/update/(?P<facet_id>.+)/$', 'cog.views.search_facet_update', name='search_facet_update'),
    url(r'^search_facet/delete/(?P<facet_id>.+)/$', 'cog.views.search_facet_delete', name='search_facet_delete'),
    url(r'^search_files/(?P<dataset_id>.+)/(?P<index_node>.+)/$', 'cog.views.search_files', name='search_files'),
    url(r'^metadata_display/(?P<project_short_name>.+)/$', 'cog.views.metadata_display', name='metadata_display' ),


    # authentication - use django auth
    #url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'cog/account/login.html'}, name='login'),
    url(r'^login/$', custom_login, {'template_name': 'cog/openid/login2.html'}, name='login'),
    # force redirection to login page after logout
    #url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    # use next=... to redirect to previous page after logout
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

    # include openid URLs
    url(r'^openid/login/$', 'django_openid_auth.views.login_begin', {'template_name': 'cog/openid/login2.html'}, name='openid-login'),
    #url(r'^openid/complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^openid/complete/$', custom_login_complete, name='openid-complete'),
    url(r'^openid/logo.gif$', 'django_openid_auth.views.logo', name='openid-logo'),

    # user management
    url(r'^user/add/$', 'cog.views.user_add', name='user_add' ),
    url(r'^user/update/(?P<user_id>\d+)/$', 'cog.views.user_update', name='user_update' ),
    url(r'^user/detail/(?P<user_id>\d+)/$', 'cog.views.user_detail', name='user_detail'),
    url(r'^password/update/(?P<user_id>\d+)/$', 'cog.views.password_update', name='password_update'),
    url(r'^password/reset/$', 'cog.views.password_reset', name='password_reset'),
    url(r'^username/reminder/$', 'cog.views.username_reminder', name='username_reminder'),
    url(r'^user/byopenid/$', 'cog.views.user_byopenid', name='user_byopenid'),
    #url(r'^user/site_update/(?P<user_id>\d+)/$', 'cog.views.site_update', name='site_update'),
    url(r'^user/profile/(?P<user_id>\d+)/$', 'cog.views.user_profile_redirect', name='user_profile_redirect'),

    # data cart
    url(r'^datacart/display/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_display', name='datacart_display'),
    url(r'^datacart/add/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_add', name='datacart_add'),
    url(r'^datacart/delete/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_delete', name='datacart_delete'),
    url(r'^datacart/empty/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_empty', name='datacart_empty'),
    url(r'^datacart/wget/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_wget', name='datacart_wget'),
    url(r'^datacart/add_all/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_add_all', name='datacart_add_all'),
    url(r'^datacart/delete_all/(?P<site_id>\d+)/(?P<user_id>\d+)/$', 'cog.views.datacart_delete_all', name='datacart_delete_all'),

    # projects
    url(r'^project/add/$', 'cog.views.project_add', name='project_add' ),
    url(r'^project/update/(?P<project_short_name>.+)/$', 'cog.views.project_update', name='project_update' ),
    url(r'^project/delete/(?P<project_short_name>.+)/$', 'cog.views.project_delete', name='project_delete' ),
    url(r'^project/index/(?P<project_short_name>.+)/$', 'cog.views.project_index', name='project_index' ),

    # news
    url(r'^news/list/(?P<project_short_name>.+)/$', 'cog.views.news_list', name='news_list'),
    url(r'^news/add/(?P<project_short_name>.+)/$', 'cog.views.news_add', name='news_add'),
    url(r'^news/detail/(?P<news_id>\d+)/$', 'cog.views.news_detail', name='news_detail'),
    url(r'^news/update/(?P<news_id>\d+)/$', 'cog.views.news_update', name='news_update'),
    url(r'^news/delete/(?P<news_id>\d+)/$', 'cog.views.news_delete', name='news_delete'),

    # posts
    url(r'^post/add/(?P<project_short_name>.+)/$', 'cog.views.post_add', name='post_add'),
    url(r'^post/update/(?P<post_id>\d+)/$', 'cog.views.post_update', name='post_update'),
    url(r'^post/detail/(?P<post_id>\d+)/$', 'cog.views.post_detail', name='post_detail'),
    url(r'^post/list/(?P<project_short_name>.+)/$', 'cog.views.post_list', name='post_list'),
    url(r'^post/delete/(?P<post_id>\d+)/$', 'cog.views.post_delete', name='post_delete'),
    url(r'^post/cancel/(?P<post_id>\d+)/$', 'cog.views.post_cancel', name='post_cancel'),

    # documents
    url(r'^doc/add/(?P<project_short_name>.+)/$', 'cog.views.doc_add', name='doc_add'),
    url(r'^doc/detail/(?P<doc_id>\d+)/$', 'cog.views.doc_detail', name='doc_detail'),
    url(r'^doc/update/(?P<doc_id>\d+)/$', 'cog.views.doc_update', name='doc_update'),
    url(r'^doc/remove/(?P<doc_id>\d+)/$', 'cog.views.doc_remove', name='doc_remove'),
    url(r'^doc/list/(?P<project_short_name>.+)/$', 'cog.views.doc_list', name='doc_list'),
     url(r'^doc/upload/(?P<project_short_name>.+)/$', 'cog.views.doc_upload', name='doc_upload'),

    # posts and documents
    url(r'^post/add_doc/(?P<post_id>\d+)/$', 'cog.views.post_add_doc', name='post_add_doc'),
    url(r'^post/remove_doc/(?P<post_id>\d+)/(?P<doc_id>\d+)/$', 'cog.views.post_remove_doc', name='post_remove_doc'),

    # signals
    url(r'^signal/list/(?P<project_short_name>.+)/$', 'cog.views.signal_list', name='signal_list'),

    # group management
    url(r'^membership/request/(?P<project_short_name>[^/]+)/$', 'cog.views.membership_request', name='membership_request' ),
    url(r'^membership/list/enrolled/(?P<project_short_name>[^/]+)/$', 'cog.views.membership_list_enrolled', name='membership_list_enrolled' ),
    url(r'^membership/list/requested/(?P<project_short_name>[^/]+)/$', 'cog.views.membership_list_requested', name='membership_list_requested' ),
    url(r'^membership/list/all/(?P<project_short_name>[^/]+)/$', 'cog.views.membership_list_all', name='membership_list_all' ),
    url(r'^membership/process/(?P<project_short_name>[^/]+)/$', 'cog.views.membership_process', name='membership_process' ),
    url(r'^membership/remove/(?P<project_short_name>[^/]+)/$', 'cog.views.membership_remove', name='membership_remove' ),

    # project tags
    url(r'^projects/(?P<project_short_name>[^/]+)/tags/update/$', 'cog.views.tags_update', name='tags_update'),

    # project browser
    url(r'^projects/(?P<project_short_name>[^/]+)/browse/(?P<tab>[^/]+)/$', 'cog.views.project_browser', name='project_browser'),

    # NAVBAR URLs
    (r'', include('cog.urls_navbar')),

    # project generic pages
    # Note: these URLs must come last because the last URL matches everything within the project!
    url(r'^projects/$', 'cog.views.index', name='unspecified_project'),
    url(r'^projects/(?P<project_short_name>[^/]+)/$', 'cog.views.project_home', name='project_home'),
    url(r'^projects/(?P<project_short_name>[^/]+)/.+$', 'cog.views.page_detail', name='page_detail'),

    # resized project media (must be served without any access control since they are not wrapped by "Doc" objects)
    url(r'^site_media/(?P<path>.*_thumbnail.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_small.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_medium.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_big.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_large.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    # project media
    url(r'^site_media/projects/(?P<path>.*)$', 'cog.views.doc_download', name='doc_download'),
    # project data
    url(r'^site_media/data/(?P<path>.*)$', 'cog.views.data_download', name='data_download'),
    
    # information shared with other sites
    url(r'^share/projects/$', 'cog.views.share_projects', name='share_projects'),
    url(r'^share/user/$', 'cog.views.share_user', name='share_user'),
    url(r'^share/sync/projects/$', 'cog.views.sync_projects', name='sync_projects'),

)
