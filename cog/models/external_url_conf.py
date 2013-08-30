'''
Module containing configuration for ExternalUrl objects.
'''

class ExternalUrlConf(object):
    '''Simple class for holding configuration information about External URL pages.'''
    
    def __init__(self, suburl, label, type):
        self.suburl = suburl
        self.label = label
        self.type = type
        
# dictionary of External URL (key, type)
EXTERNAL_URL_TYPES = {
                      "BLOG" : "blog",
                      "REPOSITORY": "repository",
                      "HOMEPAGE": "homepage",
                      "REFERENCE": "reference",
                      "TRACKER": "tracker",
                      "USECASE": "usecase",
                      "POLICY": "policy",
                      "ROADMAP": "roadmap",
                      "DOWNLOAD": "download",
                      "ADMIN_GUIDE": "admin_guide",
                      "USER_GUIDE": "user_guide",
                      "FAQ": "faq",
                      "CODE_EXAMPLE": "code_example",
                      "DEVELOPER_GUIDE": "developer_guide",
                      "DESIGN_DOCUMENT": "design_document",
                      "TESTING": "testing",
                      "CHECKLIST": "checklist",
                      "MINUTE": "minute",
                      "METRIC": "metric",
                      "RELEASE_SCHEDULE": "release_schedule",
                      }
        
# list of pre-defined External URL pages
EXTERNAL_URL_PAGES = [ ExternalUrlConf('blogs', 'Blog', EXTERNAL_URL_TYPES["BLOG"]),
                       ExternalUrlConf('repositories', 'Repositories', EXTERNAL_URL_TYPES["REPOSITORY"]),
                       ExternalUrlConf('', 'Home Page', EXTERNAL_URL_TYPES["HOMEPAGE"]),
                       ExternalUrlConf('', 'Reference', EXTERNAL_URL_TYPES["REFERENCE"]),
                       ExternalUrlConf('trackers', 'Tracker', EXTERNAL_URL_TYPES["TRACKER"]),   
                       ExternalUrlConf('usecases', 'Use Case', EXTERNAL_URL_TYPES["USECASE"]),
                       ExternalUrlConf('policies',' Policies', EXTERNAL_URL_TYPES["POLICY"]), 
                       ExternalUrlConf('roadmap', 'Roadmap', EXTERNAL_URL_TYPES["ROADMAP"]), 
                       ExternalUrlConf('download', 'Download', EXTERNAL_URL_TYPES["DOWNLOAD"]),
                       ExternalUrlConf('admin_guide', 'Administrator\'s Guide', EXTERNAL_URL_TYPES["ADMIN_GUIDE"]),    
                       ExternalUrlConf('user_guide', 'User\'s Guide', EXTERNAL_URL_TYPES["USER_GUIDE"]), 
                       ExternalUrlConf('faq', 'FAQ', EXTERNAL_URL_TYPES["FAQ"]), 
                       ExternalUrlConf('code_examples', 'Code Examples', EXTERNAL_URL_TYPES["CODE_EXAMPLE"]),
                       ExternalUrlConf('developer_guide', 'Developer\'s Guide', EXTERNAL_URL_TYPES["DEVELOPER_GUIDE"]), 
                       ExternalUrlConf('design_docs', 'Design Documents', EXTERNAL_URL_TYPES["DESIGN_DOCUMENT"]),
                       ExternalUrlConf('testing', 'Testing', EXTERNAL_URL_TYPES["TESTING"]),
                       ExternalUrlConf('checklist', 'Checklist', EXTERNAL_URL_TYPES["CHECKLIST"]), 
                       ExternalUrlConf('minutes', 'Minutes', EXTERNAL_URL_TYPES["MINUTE"]),
                       ExternalUrlConf('metrics', 'Metrics', EXTERNAL_URL_TYPES["METRIC"]),
                       ExternalUrlConf('release_schedules', 'Release Schedules', EXTERNAL_URL_TYPES["RELEASE_SCHEDULE"]),
]

# map frm suburl -> ExternalUrlConf instance
EXTERNAL_URL_SUBURL_MAP = {}
# map from type -> ExternalUrlConf instance
EXTERNAL_URL_TYPE_MAP = {}
for obj in EXTERNAL_URL_PAGES:
    EXTERNAL_URL_SUBURL_MAP[obj.suburl] = obj
    EXTERNAL_URL_TYPE_MAP[obj.suburl] = obj

def external_url_choices():
    '''Provides valid options when building ExternalUrl choices.'''
    return [(obj.type, obj.label) for obj in EXTERNAL_URL_PAGES]