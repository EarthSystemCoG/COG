'''
Module containing configuration for ExternalUrl objects.
'''

class ExternalUrlPage(object):
    '''Simple class for holding configuration information about External URL pages.'''
    
    def __init__(self, suburl, label, type):
        self.suburl = suburl
        self.label = label
        self.type = type
        
# list of pre-defined External URL pages
EXTERNAL_URL_PAGES = [ ExternalUrlPage('blogs','Blog','blog'),
                       ExternalUrlPage('repositories','Repositories','repository'),
                       ExternalUrlPage('','Home Page','homepage'),
                       ExternalUrlPage('','Reference','reference'),
                       ExternalUrlPage('trackers','Tracker','tracker'),   
                       ExternalUrlPage('usecases','Use Case','usecase'),
                       ExternalUrlPage('policies','Policy','policy'), 
                       ExternalUrlPage('roadmap','Roadmap','roadmap'), 
                       ExternalUrlPage('download','Download','download'),
                       ExternalUrlPage('admin_guide','Administrator\'s Guide','admin_guide'),    
                       ExternalUrlPage('user_guide','User\'s Guide','user_guide'), 
                       ExternalUrlPage('faq','FAQ','faq'), 
                       ExternalUrlPage('code_examples','Code Examples','code_example'),
                       ExternalUrlPage('developer_guide','Developer\'s Guide','developer_guide'), 
                       ExternalUrlPage('design_docs','Design Documents','design_document'),
                       ExternalUrlPage('testing','Testing','testing'),
                       ExternalUrlPage('checklist','Checklist','checkclist'), 
]

# map frm suburl -> ExternalUrlPage instance
EXTERNAL_URL_PAGE_MAP = {}
for obj in EXTERNAL_URL_PAGES:
    EXTERNAL_URL_PAGE_MAP[obj.suburl] = obj

def external_url_choices():
    '''Provides valid options when building ExternalUrl choices.'''
    return [(obj.type, obj.label) for obj in EXTERNAL_URL_PAGES]