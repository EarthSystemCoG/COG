'''
Module containing URL mappong for project upper Navigational Bar.
'''
from django.conf.urls.defaults import *
from cog.models import *

urlpatterns = patterns('',
                       
    # "ABOUT US"
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>aboutus)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>aboutus)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>mission)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>mission)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),    
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>vision)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>vision)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>values)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>values)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>impacts)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>impacts)/update/$', 'cog.views.impacts_update', name='impacts_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>history)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>history)/update/$', 'cog.views.aboutus_update', name='aboutus_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>partners)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>partners)/update/$', 'cog.views.partners_update', name='partners_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>sponsors)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>sponsors)/update/$', 'cog.views.sponsors_update', name='sponsors_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>people)/$', 'cog.views.aboutus_display', name='aboutus_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>people)/update/$', 'cog.views.people_update', name='people_update'),    

        
    # "SOFTWARE"
    url(r'^projects/(?P<project_short_name>[^/]+)/software/$', 'cog.views.software_display', name='software_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/software/update/$', 'cog.views.software_update', name='software_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>download)/update/$', 'cog.views.external_urls_update', name='download_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>download)/$', 'cog.views.external_urls_display', name='download_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>admin_docs)/update/$', 'cog.views.external_urls_update', name='admin_docs_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>admin_docs)/$', 'cog.views.external_urls_display', name='admin_docs_display'),
    
    
    # "USERS"
    url(r'^projects/(?P<project_short_name>[^/]+)/users/$', 'cog.views.users_display', name='users_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/users/update/$', 'cog.views.users_update', name='users_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>faq)/update/$', 'cog.views.external_urls_update', name='faq_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>faq)/$', 'cog.views.external_urls_display', name='faq_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>user_docs)/update/$', 'cog.views.external_urls_update', name='user_docs_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>user_docs)/$', 'cog.views.external_urls_display', name='user_docs_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>code_examples)/update/$', 'cog.views.external_urls_update', name='code_examples_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>code_examples)/$', 'cog.views.external_urls_display', name='code_examples_display'),

    
    # "DEVELOPERS"   
    url(r'^projects/(?P<project_short_name>[^/]+)/developers/update/$', 'cog.views.development_update', name='development_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/developers/$', 'cog.views.development_display', name='development_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>repositories)/update/$', 'cog.views.external_urls_update', name='repositories_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>repositories)/$', 'cog.views.external_urls_display', name='repositories_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>trackers)/update/$', 'cog.views.external_urls_update', name='trackers_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>trackers)/$', 'cog.views.external_urls_display', name='trackers_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>dev_docs)/update/$', 'cog.views.external_urls_update', name='dev_docs_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>dev_docs)/$', 'cog.views.external_urls_display', name='dev_docs_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>design_docs)/update/$', 'cog.views.external_urls_update', name='design_docs_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>design_docs)/$', 'cog.views.external_urls_display', name='design_docs_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>testing)/update/$', 'cog.views.external_urls_update', name='testing_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>testing)/$', 'cog.views.external_urls_display', name='testing_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>usecases)/update/$', 'cog.views.external_urls_update', name='usecases_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>usecases)/$', 'cog.views.external_urls_display', name='usecases_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>checklist)/update/$', 'cog.views.external_urls_update', name='checklist_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>checklist)/$', 'cog.views.external_urls_display', name='checklist_display'),

        
    # "PLANS"
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>plans)/update/$', 'cog.views.external_urls_update', name='plans_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>plans)/$', 'cog.views.external_urls_display', name='plans_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/future_work/$', 'cog.views.future_work_display', name='future_work_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/future_work/update/$', 'cog.views.future_work_update', name='future_work_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>roadmap)/update/$', 'cog.views.external_urls_update', name='roadmap_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>roadmap)/$', 'cog.views.external_urls_display', name='roadmap_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>release_schedules)/update/$', 'cog.views.external_urls_update', name='release_schedules_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>release_schedules)/$', 'cog.views.external_urls_display', name='release_schedules_display'),


 
    # GOVERNANCE
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>governance)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>bodies)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>roles)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>communication)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<tab>processes)/$', 'cog.views.governance_display', name='governance_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/governance/update/$', 'cog.views.governance_overview_update', name='governance_overview_update'),           
    url(r'^projects/(?P<project_short_name>[^/]+)/bodies/update/(?P<category>[^/]+)/$', 'cog.views.management_body_update', name='management_body_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bodies/update/members/(?P<object_id>[^/]+)/$', 'cog.views.management_body_members', name='management_body_members'),
    url(r'^projects/(?P<project_short_name>[^/]+)/communication/update/$', 'cog.views.communication_means_update', name='communication_means_update'),    
    url(r'^communication_means/(?P<object_id>[^/]+)/members/$', 'cog.views.communication_means_members', name='communication_means_members'),
    url(r'^projects/(?P<project_short_name>[^/]+)/processes/update/$', 'cog.views.processes_update', name='governance_processes_update'),    
    url(r'^projects/(?P<project_short_name>[^/]+)/roles/update/$', 'cog.views.organizational_role_update', name='organizational_role_update'),
    url(r'^organizational_role/(?P<object_id>[^/]+)/members/$', 'cog.views.organizational_role_members', name='organizational_role_members'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>policies)/update/$', 'cog.views.external_urls_update', name='policies_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>policies)/$', 'cog.views.external_urls_display', name='policies_display'),    
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>minutes)/update/$', 'cog.views.external_urls_update', name='minutes_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>minutes)/$', 'cog.views.external_urls_display', name='minutes_display'),
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>metrics)/update/$', 'cog.views.external_urls_update', name='metrics_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/(?P<suburl>metrics)/$', 'cog.views.external_urls_display', name='metrics_display'),


    # "RESOURCES" (aka bookmarks and folders)
    url(r'^projects/(?P<project_short_name>[^/]+)/resources/$', 'cog.views.bookmark_list', name='bookmark_list'),
        
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/add/$', 'cog.views.bookmark_add', name='bookmark_add'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/add2/$', 'cog.views.bookmark_add2', name='bookmark_add2'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/update/(?P<bookmark_id>[^/]+)/$', 'cog.views.bookmark_update', name='bookmark_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/delete/(?P<bookmark_id>[^/]+)/$', 'cog.views.bookmark_delete', name='bookmark_delete'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/folders/add/$', 'cog.views.folder_add', name='folder_add'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/folders/update/(?P<folder_id>[^/]+)/$', 'cog.views.folder_update', name='folder_update'),
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/folders/delete/(?P<folder_id>[^/]+)/$', 'cog.views.folder_delete', name='folder_delete'),
    
    url(r'^projects/(?P<project_short_name>[^/]+)/bookmarks/add_notes/(?P<bookmark_id>[^/]+)/$', 'cog.views.bookmark_add_notes', name='bookmark_add_notes'),   
    
    # "CONTACT US"
    url(r'^projects/(?P<project_short_name>[^/]+)/contactus/update/$', 'cog.views.contactus_update', name='contactus_update'),   
    url(r'^projects/(?P<project_short_name>[^/]+)/contactus/$', 'cog.views.contactus_display', name='contactus_display'),
             
)
