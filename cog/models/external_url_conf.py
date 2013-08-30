'''
Module containing configuration for ExternalUrl objects.
'''

class ExternalUrlConf(object):
    '''Simple class for holding configuration information about External URL pages.'''
    
    def __init__(self, suburl, label, type):
        self.suburl = suburl
        self.label = label
        self.type = type
        
# list of pre-defined External URL pages
EXTERNAL_URL_PAGES = [ ExternalUrlConf('blogs','Blog','blog'),
                       ExternalUrlConf('repositories','Repositories','repository'),
                       ExternalUrlConf('','Home Page','homepage'),
                       ExternalUrlConf('','Reference','reference'),
                       ExternalUrlConf('trackers','Tracker','tracker'),   
                       ExternalUrlConf('usecases','Use Case','usecase'),
                       ExternalUrlConf('policies','Policies','policy'), 
                       ExternalUrlConf('roadmap','Roadmap','roadmap'), 
                       ExternalUrlConf('download','Download','download'),
                       ExternalUrlConf('admin_guide','Administrator\'s Guide','admin_guide'),    
                       ExternalUrlConf('user_guide','User\'s Guide','user_guide'), 
                       ExternalUrlConf('faq','FAQ','faq'), 
                       ExternalUrlConf('code_examples','Code Examples','code_example'),
                       ExternalUrlConf('developer_guide','Developer\'s Guide','developer_guide'), 
                       ExternalUrlConf('design_docs','Design Documents','design_document'),
                       ExternalUrlConf('testing','Testing','testing'),
                       ExternalUrlConf('checklist','Checklist','checkclist'), 
                       ExternalUrlConf('minutes','Minutes','minute'),
                       ExternalUrlConf('metrics','Metrics','metric'),
                       ExternalUrlConf('release_schedules','Release Schedules','release_schedule'),
]

# map frm suburl -> ExternalUrlConf instance
EXTERNAL_URL_PAGE_MAP = {}
for obj in EXTERNAL_URL_PAGES:
    EXTERNAL_URL_PAGE_MAP[obj.suburl] = obj

def external_url_choices():
    '''Provides valid options when building ExternalUrl choices.'''
    return [(obj.type, obj.label) for obj in EXTERNAL_URL_PAGES]