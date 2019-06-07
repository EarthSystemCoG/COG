from django.conf.urls import url, include
import cog.views
import django_openid_auth.views
import django.contrib.auth.views
import django.views
from cog.models import settings


urlpatterns = [

    # FIXME: top-level index
    #url(r'^index/$', TemplateView.as_view(template_name="cog/index.html")),
        
    # site home
    url(r'^$', cog.views.site_home, name='site_home' ) ,
    
    # COG administration
    url(r'^cogadmin/projects/$', cog.views.admin_projects, name='admin_projects' ),
    url(r'^cogadmin/peers/$', cog.views.admin_peers, name='admin_peers' ),
    url(r'^cogadmin/users/$', cog.views.admin_users, name='admin_users' ),
    
    url(r'^search/(?P<project_short_name>.+)/$', cog.views.search, name='search' ),
    url(r'^search_profile/config/(?P<project_short_name>.+)/$', cog.views.search_profile_config, name='search_profile_config'),
    url(r'^search_profile/export/(?P<project_short_name>.+)/$', cog.views.search_profile_export, name='search_profile_export'),
    url(r'^search_profile/import/(?P<project_short_name>.+)/$', cog.views.search_profile_import, name='search_profile_import'),
    url(r'^search_profile/order/(?P<project_short_name>.+)/$', cog.views.search_profile_order, name='search_profile_order' ),
    url(r'^search_facet/add/(?P<project_short_name>.+)/$', cog.views.search_facet_add, name='search_facet_add'),
    url(r'^search_facet/update/(?P<facet_id>.+)/$', cog.views.search_facet_update, name='search_facet_update'),
    url(r'^search_facet/delete/(?P<facet_id>.+)/$', cog.views.search_facet_delete, name='search_facet_delete'),
    url(r'^search_group/add/(?P<project_short_name>.+)/$', cog.views.search_group_add, name='search_group_add'),
    url(r'^search_group/update/(?P<group_id>.+)/$', cog.views.search_group_update, name='search_group_update'),
    url(r'^search_group/delete/(?P<group_id>.+)/$', cog.views.search_group_delete, name='search_group_delete'),
    url(r'^search_files/(?P<dataset_id>.+)/(?P<index_node>.+)/$', cog.views.search_files, name='search_files'),
    url(r'^metadata_display/(?P<project_short_name>.+)/$', cog.views.metadata_display, name='metadata_display' ),
    url(r'^search_reload/$', cog.views.search_reload, name='search_reload' ),
    url(r'^citation_display/$', cog.views.citation_display, name='citation_display'),

    # authentication options
    # a) django (username/password) login
    #url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'cog/account/login.html'}, name='login'),
    url(r'^login2/$', django.contrib.auth.views.login, {'template_name': 'cog/account/login.html'}, name='login'),
    
    # b) combined django + openid login
    #url(r'^login/$', custom_login, {'template_name': 'cog/openid/login2.html'}, name='login'),
    #url(r'^openid/login/$', 'django_openid_auth.views.login_begin', {'template_name': 'cog/openid/login2.html'}, name='openid-login'),
    
    # c) openid-only login
    url(r'^login/$', cog.views.custom_login, {'template_name': 'cog/openid/login.html'}, name='login'),
    url(r'^openid/login/$', django_openid_auth.views.login_begin, {'template_name': 'cog/openid/login.html'}, name='openid-login'),
    
    # b) or c)
    #url(r'^openid/complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^openid/complete/$', cog.views.custom_login_complete, name='openid-complete'),
    url(r'^openid/logo.gif$', django_openid_auth.views.logo, name='openid-logo'),

    
    # force redirection to login page after logout
    #url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    # use next=... to redirect to previous page after logout
    url(r'^logout/$', django.contrib.auth.views.logout, name='logout'),

    # user management
    url(r'^user/add/$', cog.views.user_add, name='user_add' ),
    url(r'^user/update/(?P<user_id>\d+)/$', cog.views.user_update, name='user_update' ),
    url(r'^user/delete/(?P<user_id>\d+)/$', cog.views.user_delete, name='user_delete' ),
    url(r'^user/detail/(?P<user_id>\d+)/$', cog.views.user_detail, name='user_detail'),
    url(r'^password/update/(?P<user_id>\d+)/$', cog.views.password_update, name='password_update'),
    url(r'^password/reset/$', cog.views.password_reset, name='password_reset'),
    url(r'^user/reminder/$', cog.views.user_reminder, name='user_reminder'),
    url(r'^user/byopenid/$', cog.views.user_byopenid, name='user_byopenid'),
    url(r'^user/image/$', cog.views.user_image, name='user_image'),
    url(r'^user/profile/(?P<user_id>\d+)/$', cog.views.user_profile_redirect, name='user_profile_redirect'),
    

    # data cart
    url(r'^datacart/display/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_display, name='datacart_display'),
    url(r'^datacart/add/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_add, name='datacart_add'),
    url(r'^datacart/delete/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_delete, name='datacart_delete'),
    url(r'^datacart/empty/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_empty, name='datacart_empty'),
    url(r'^datacart/wget/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_wget, name='datacart_wget'),
    url(r'^datacart/add_all/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_add_all, name='datacart_add_all'),
    url(r'^datacart/delete_all/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_delete_all, name='datacart_delete_all'),
    url(r'^datacart/byopenid/$', cog.views.datacart_byopenid, name='datacart_byopenid'),
    url(r'^datacart/datacart-pid/(?P<site_id>\d+)/(?P<user_id>\d+)/$', cog.views.datacart_pid, name='datacart_pid'),

    # projects
    url(r'^project/add/$', cog.views.project_add, name='project_add' ),
    url(r'^project/update/(?P<project_short_name>.+)/$', cog.views.project_update, name='project_update' ),
    url(r'^project/delete/(?P<project_short_name>.+)/$', cog.views.project_delete, name='project_delete' ),
    url(r'^project/index/(?P<project_short_name>.+)/$', cog.views.project_index, name='project_index' ),

    # news
    url(r'^news/list/(?P<project_short_name>.+)/$', cog.views.news_list, name='news_list'),
    url(r'^news/add/(?P<project_short_name>.+)/$', cog.views.news_add, name='news_add'),
    url(r'^news/detail/(?P<news_id>\d+)/$', cog.views.news_detail, name='news_detail'),
    url(r'^news/update/(?P<news_id>\d+)/$', cog.views.news_update, name='news_update'),
    url(r'^news/delete/(?P<news_id>\d+)/$', cog.views.news_delete, name='news_delete'),

    # posts
    url(r'^post/add/(?P<project_short_name>.+)/$', cog.views.post_add, name='post_add'),
    url(r'^post/update/(?P<post_id>\d+)/$', cog.views.post_update, name='post_update'),
    url(r'^post/detail/(?P<post_id>\d+)/$', cog.views.post_detail, name='post_detail'),
    url(r'^post/list/(?P<project_short_name>.+)/$', cog.views.post_list, name='post_list'),
    url(r'^post/delete/(?P<post_id>\d+)/$', cog.views.post_delete, name='post_delete'),
    url(r'^post/cancel/(?P<post_id>\d+)/$', cog.views.post_cancel, name='post_cancel'),

    # documents
    url(r'^doc/add/(?P<project_short_name>.+)/$', cog.views.doc_add, name='doc_add'),
    url(r'^doc/detail/(?P<doc_id>\d+)/$', cog.views.doc_detail, name='doc_detail'),
    url(r'^doc/update/(?P<doc_id>\d+)/$', cog.views.doc_update, name='doc_update'),
    url(r'^doc/remove/(?P<doc_id>\d+)/$', cog.views.doc_remove, name='doc_remove'),
    url(r'^doc/list/(?P<project_short_name>.+)/$', cog.views.doc_list, name='doc_list'),
     url(r'^doc/upload/(?P<project_short_name>.+)/$', cog.views.doc_upload, name='doc_upload'),

    # posts and documents
    url(r'^post/add_doc/(?P<post_id>\d+)/$', cog.views.post_add_doc, name='post_add_doc'),
    url(r'^post/remove_doc/(?P<post_id>\d+)/(?P<doc_id>\d+)/$', cog.views.post_remove_doc, name='post_remove_doc'),

    # signals
    url(r'^signal/list/(?P<project_short_name>.+)/$', cog.views.signal_list, name='signal_list'),

    # project membership
    url(r'^membership/request/(?P<project_short_name>[^/]+)/$', cog.views.membership_request, name='membership_request' ),
    url(r'^membership/list/enrolled/(?P<project_short_name>[^/]+)/$', cog.views.membership_list_enrolled, name='membership_list_enrolled' ),
    url(r'^membership/list/requested/(?P<project_short_name>[^/]+)/$', cog.views.membership_list_requested, name='membership_list_requested' ),
    url(r'^membership/list/all/(?P<project_short_name>[^/]+)/$', cog.views.membership_list_all, name='membership_list_all' ),
    url(r'^membership/process/(?P<project_short_name>[^/]+)/$', cog.views.membership_process, name='membership_process' ),
    url(r'^membership/remove/(?P<project_short_name>[^/]+)/$', cog.views.membership_remove, name='membership_remove' ),
    
    # group membership (data access control)
    url(r'^ac/subscribe/(?P<group_name>[^/]+)/$', cog.views.ac_subscribe, name='ac_subscribe' ),
    url(r'^ac/process/(?P<group_name>[^/]+)/(?P<user_id>\d+)/$', cog.views.ac_process, name='ac_process' ),
    url(r'^ac/list/$', cog.views.ac_list, name='ac_list' ),

    # project tags
    url(r'^projects/(?P<project_short_name>[^/]+)/tags/update/$', cog.views.tags_update, name='tags_update'),

    # project browser
    url(r'^project_browser/(?P<project_short_name>[^/]+)/browse/(?P<tab>[^/]+)/$', cog.views.project_browser, name='project_browser'),
    # the following matches on Apache httpd
    url(r'^project_browser/browse/(?P<tab>[^/]+)/$', cog.views.project_empty_browser, name='project_empty_browser'),
    # the following matches on django development server
    url(r'^project_browser//browse/(?P<tab>[^/]+)/$', cog.views.project_empty_browser, name='project_empty_browser'),
    # save/delete user tags
    url(r'^project_browser/save_user_tag/', cog.views.save_user_tag, name='save_user_tag'),
    url(r'^project_browser/delete_user_tag/', cog.views.delete_user_tag, name='delete_user_tag'),

    # NAVBAR URLs
    url(r'', include('cog.urls_navbar')),

    # project generic pages
    # Note: these URLs must come last because the last URL matches everything within the project!
    #url(r'^projects/$', 'cog.views.index', name='unspecified_project'),
    url(r'^projects/(?P<project_short_name>[^/]+)/$', cog.views.project_home, name='project_home'),
    url(r'^projects/(?P<project_short_name>[^/]+)/.+$', cog.views.page_detail, name='page_detail'),

    # resized project media (must be served without any access control since they are not wrapped by "Doc" objects)
    url(r'^site_media/(?P<path>.*_thumbnail.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_small.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_medium.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_big.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    #url(r'^site_media/(?P<path>.*_large.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    # project media
    url(r'^site_media/projects/(?P<path>.*)$', cog.views.doc_download, name='doc_download'),
    # project data
    #url(r'^site_media/data/(?P<path>.*)$', 'cog.views.data_download', name='data_download'),
    
    # information shared with other sites
    url(r'^share/projects/$', cog.views.share_projects, name='share_projects'),
    url(r'^share/groups/$', cog.views.share_groups, name='share_groups'),
    url(r'^share/user/$', cog.views.share_user, name='share_user'),
    url(r'^share/sync/projects/$', cog.views.sync_projects, name='sync_projects'),
        
    # Globus integration
    url(r'^globus/download/$', cog.views.views_globus.download, name='globus_download'),
    url(r'^globus/transfer/$', cog.views.views_globus.transfer, name='globus_transfer'),
    url(r'^globus/oauth/$', cog.views.views_globus.oauth, name='globus_oauth'),
    url(r'^globus/token/$', cog.views.views_globus.token, name='globus_token'),
    url(r'^globus/submit/$', cog.views.views_globus.submit, name='globus_submit'),
    url(r'^globus/script/$', cog.views.views_globus.script, name='globus_script'),    
    url(r'^status/$', cog.views.node_status, name='node_status'),

]
