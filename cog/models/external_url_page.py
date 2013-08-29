'''
Module containing configuration for ExternalUrl objects.
'''

class ExternalUrlPage(object):
    '''Simple class for holding configuration information about External URL pages.'''
    
    def __init__(self, suburl, label, type):
        self.suburl = suburl
        self.label = label
        self.type = type
        
EXTERNAL_URL_PAGES = {  
    'URL_TYPE_BLOG': ExternalUrlPage('blogs','Blog','blog'),
    'URL_TYPE_REPOSITORY': ExternalUrlPage('repositories','Repositories','repository'),
    'URL_TYPE_HOMEPAGE': ExternalUrlPage('','Home Page','homepage'),
    'URL_TYPE_REFERENCE': ExternalUrlPage('','Reference','reference'),
    'URL_TYPE_TRACKER': ExternalUrlPage('trackers','Tracker','tracker'),   
    'URL_TYPE_USECASE': ExternalUrlPage('usecases','Use Case','usecase'),
    'URL_TYPE_POLICY': ExternalUrlPage('policies','Policy','policy'),
    'URL_TYPE_ROADMAP': ExternalUrlPage('roadmap','Roadmap','roadmap'), 
    'URL_TYPE_DOWNLOAD': ExternalUrlPage('download','Download','download'),
    'URL_TYPE_ADMIN_GUIDE': ExternalUrlPage('admin_guide','Administrator\'s Guide','admin_guide'),    
    'URL_TYPE_USER_GUIDE': ExternalUrlPage('user_guide','User\'s Guide','user_guide'), 
    'URL_TYPE_FAQ': ExternalUrlPage('faq','FAQ','faq'), 
    'URL_TYPE_CODE_EXAMPLE': ExternalUrlPage('code_examples','Code Examples','code_examples'),
    'URL_TYPE_DEVELOPER_GUIDE': ExternalUrlPage('developer_guide','Developer\'s Guide','developer_guide'),
    'URL_TYPE_DESIGN_DOC': ExternalUrlPage('design_docs','Design Documents','design_document'),
    'URL_TYPE_TESTING': ExternalUrlPage('testing','Testing','testing'),
    'URL_TYPE_CHECKLIST': ExternalUrlPage('checklist','Checklist','checkclist'), 
}

def external_url_choices():
    '''Provides valid options when building ExternalUrl choices.'''
    return [(obj.type, obj.label) for (key,obj) in EXTERNAL_URL_PAGES.items()]