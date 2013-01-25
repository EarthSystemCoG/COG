from django.conf.urls.defaults import *
from cog.models import *

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
    
    # authentication - use django auth
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'cog/account/login.html'}, name='login'),
    # force redirection to login page after logout
    #url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    # use next=... to redirect to previous page after logout
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

    # user management
    url(r'^user/add/$', 'cog.views.user_add', name='user_add' ),
    url(r'^user/update/(?P<user_id>\d+)/$', 'cog.views.user_update', name='user_update' ),
    url(r'^user/detail/(?P<user_id>\d+)/$', 'cog.views.user_detail', name='user_detail'),
    url(r'^password/update/(?P<user_id>\d+)/$', 'cog.views.password_update', name='password_update'),
    url(r'^password/reset/$', 'cog.views.password_reset', name='password_reset'),
    url(r'^username/reminder/$', 'cog.views.username_reminder', name='username_reminder'),

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
    
    # pages
    #url(r'^page/add/(?P<project_short_name>.+)/$', 'cog.views.page_add', name='page_add'),
    #url(r'^page/(?P<project_short_name>[^/]+)/.+/$', 'cog.views.page_detail', name='page_detail'),
    
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
    
        
    # "About Us" pages: aboutus, mission, vision, values, partners, sponsors, people
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>aboutus)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>aboutus)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>mission)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>mission)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),    
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>vision)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>vision)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>values)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>values)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>partners)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>partners)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>sponsors)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>sponsors)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>people)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>people)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),

    # "Development" pages: development, code and trackers    
    url(r'^projects/(?P<project_short_name>[^/]+)/development/update/$', 'cog.views.development_update', name='development_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/development/$', 'cog.views.development_display', name='development_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/trackers/update/$', 'cog.views.trackers_update', name='trackers_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/trackers/$', 'cog.views.trackers_display', name='trackers_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/code/update/$', 'cog.views.code_update', name='code_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/code/$', 'cog.views.code_display', name='code_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/usecases/update/$', 'cog.views.usecases_update', name='usecases_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/usecases/$', 'cog.views.usecases_display', name='usecases_display'),


    # folders and bookmarks
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/$', 'cog.views.bookmark_list', name='bookmark_list'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/add/$', 'cog.views.bookmark_add', name='bookmark_add'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/add2/$', 'cog.views.bookmark_add2', name='bookmark_add2'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/update/(?P<bookmark_id>[^/]+)/$', 'cog.views.bookmark_update', name='bookmark_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/delete/(?P<bookmark_id>[^/]+)/$', 'cog.views.bookmark_delete', name='bookmark_delete'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/folders/add/$', 'cog.views.folder_add', name='folder_add'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/folders/update/(?P<folder_id>[^/]+)/$', 'cog.views.folder_update', name='folder_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/folders/delete/(?P<folder_id>[^/]+)/$', 'cog.views.folder_delete', name='folder_delete'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/add_notes/(?P<bookmark_id>[^/]+)/$', 'cog.views.bookmark_add_notes', name='bookmark_add_notes'),

    # project 'get involved'
    url(r'^projects/(?P<project_short_name>[^/]+)/getinvolved/update/$', 'cog.views.getinvolved_update', name='getinvolved_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/getinvolved/$', 'cog.views.getinvolved_display', name='getinvolved_display'),
   
    # project "contact us"
    url(r'^projects/(?P<project_short_name>[^/]+)/contactus/update/$', 'cog.views.contactus_update', name='contactus_update'),   
    # FIXME: uncomment when object model is available
    #url(r'^projects/(?P<project_short_name>[^/]+)/contactus/$', 'cog.views.contactus_display', name='contactus_display'),
    
    # project "support"
    url(r'^projects/(?P<project_short_name>[^/]+)/support/update/$', 'cog.views.support_update', name='support_update'),
    # FIXME: uncomment when object model is available
    #url(r'^projects/(?P<project_short_name>[^/]+)/support/$', 'cog.views.support_display', name='support_display'),   
       
    
    # project policies
    #url(r'^projects/(?P<project_short_name>[^/]+)/processes/update/policies/$', 'cog.views.policies_update', name='policies_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/policies/update/$', 'cog.views.policies_update', name='policies_update'),
   
    # project roadmap
    url(r'^projects/(?P<project_short_name>[^/]+)/roadmap/update/$', 'cog.views.roadmap_update', name='roadmap_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/roadmap/$', 'cog.views.roadmap_display', name='roadmap_display'),

    # project governance
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>governance)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>bodies)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>roles)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>communication)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>processes)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>policies)/$', 'cog.views.governance_display', name='governance_display'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/governance/update/$', 'cog.views.governance_overview_update', name='governance_overview_update'),    
       
    url(r'^projects/(?P<project_short_name>[^/]+)/bodies/update/(?P<category>[^/]+)/$', 'cog.views.management_body_update', name='management_body_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bodies/update/members/(?P<object_id>[^/]+)/$', 'cog.views.management_body_members', name='management_body_members'),
    
    #url(r'^projects/(?P<project_short_name>[^/]+)/processes/update/communication_means/(?P<internal>[^/]+)/$', 'cog.views.communication_means_update', name='communication_means_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/communication/update/(?P<internal>[^/]+)/$', 'cog.views.communication_means_update', name='communication_means_update'),    
    url(r'^communication_means/(?P<object_id>[^/]+)/members/$', 'cog.views.communication_means_members', name='communication_means_members'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/processes/update/$', 'cog.views.processes_update', name='governance_processes_update'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/roles/update/$', 'cog.views.organizational_role_update', name='organizational_role_update'),
    url(r'^organizational_role/(?P<object_id>[^/]+)/members/$', 'cog.views.organizational_role_members', name='organizational_role_members'),
  
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
    
)
