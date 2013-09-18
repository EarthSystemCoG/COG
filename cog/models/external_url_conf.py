'''
Module containing configuration for ExternalUrl objects.
'''

# dictionary of External URL (key, type)
EXTERNAL_URL_TYPES = {
                      "BLOG" : "blog",
                      "REPOSITORY": "repository",
                      "HOMEPAGE": "homepage",
                      "REFERENCE": "reference",
                      "TRACKER": "tracker",
                      "USECASE": "usecase",
                      "POLICY": "policy",
                      "PLANS": "plans",
                      "ROADMAPS": "roadmaps",
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

class ExternalUrlConf(object):
    '''Simple class for holding configuration information about External URL pages.'''
    
    def __init__(self, suburl, label, type):
        self.suburl = suburl
        self.label = label
        self.type = type
        
class ExternalUrlManager(object):
    '''Class managing configuration for External URLs.'''
    
    def __init__(self):
                
        # list of pre-defined External URL pages
        self.EXTERNAL_URL_PAGES = [ ExternalUrlConf('blogs', 'Blog', EXTERNAL_URL_TYPES["BLOG"]),
                                    ExternalUrlConf('repositories', 'Repositories', EXTERNAL_URL_TYPES["REPOSITORY"]),
                                    ExternalUrlConf('', 'Home Page', EXTERNAL_URL_TYPES["HOMEPAGE"]),
                                    ExternalUrlConf('', 'Reference', EXTERNAL_URL_TYPES["REFERENCE"]),
                                    ExternalUrlConf('trackers', 'Tracker', EXTERNAL_URL_TYPES["TRACKER"]),   
                                    ExternalUrlConf('usecases', 'Use Case', EXTERNAL_URL_TYPES["USECASE"]),
                                    ExternalUrlConf('policies',' Policies', EXTERNAL_URL_TYPES["POLICY"]), 
                                    ExternalUrlConf('plans', 'Plans', EXTERNAL_URL_TYPES["PLANS"]), 
                                    ExternalUrlConf('roadmap', 'Roadmaps', EXTERNAL_URL_TYPES["ROADMAPS"]), 
                                    ExternalUrlConf('download', 'Download / Releases', EXTERNAL_URL_TYPES["DOWNLOAD"]),
                                    ExternalUrlConf('admin_guide', 'Installer / Admin Guide', EXTERNAL_URL_TYPES["ADMIN_GUIDE"]),    
                                    ExternalUrlConf('user_guide', 'User Guide', EXTERNAL_URL_TYPES["USER_GUIDE"]), 
                                    ExternalUrlConf('faq', 'FAQ', EXTERNAL_URL_TYPES["FAQ"]), 
                                    ExternalUrlConf('code_examples', 'Code Examples', EXTERNAL_URL_TYPES["CODE_EXAMPLE"]),
                                    ExternalUrlConf('developer_guide', 'Dev Guide', EXTERNAL_URL_TYPES["DEVELOPER_GUIDE"]), 
                                    ExternalUrlConf('design_docs', 'Design', EXTERNAL_URL_TYPES["DESIGN_DOCUMENT"]),
                                    ExternalUrlConf('testing', 'Testing', EXTERNAL_URL_TYPES["TESTING"]),
                                    ExternalUrlConf('checklist', 'Checklists', EXTERNAL_URL_TYPES["CHECKLIST"]), 
                                    ExternalUrlConf('minutes', 'Minutes', EXTERNAL_URL_TYPES["MINUTE"]),
                                    ExternalUrlConf('metrics', 'Metrics', EXTERNAL_URL_TYPES["METRIC"]),
                                    ExternalUrlConf('release_schedules', 'Release Schedules', EXTERNAL_URL_TYPES["RELEASE_SCHEDULE"]),
                                  ]
        
        # map frm suburl -> ExternalUrlConf instance
        self.EXTERNAL_URL_SUBURL_MAP = {}
        
        # map from type -> ExternalUrlConf instance
        self.EXTERNAL_URL_TYPE_MAP = {}
        
        for obj in self.EXTERNAL_URL_PAGES:
            self.EXTERNAL_URL_SUBURL_MAP[obj.suburl] = obj
            self.EXTERNAL_URL_TYPE_MAP[obj.type] = obj
            
    def getConf(self, suburl=None, type=None):
        '''Returns the configuration for a given type (checked first), suburl (checked second), or None.'''
        
        if type is not None:
            return  self.EXTERNAL_URL_TYPE_MAP[type]
        elif suburl is not None:
            return  self.EXTERNAL_URL_SUBURL_MAP[suburl]
        else:
            raise Exception("Suburl or type must be specified")
            
    def external_url_choices(self):
        '''Provides valid options when building ExternalUrl choices.'''
        
        return [(obj.type, obj.label) for obj in self.EXTERNAL_URL_PAGES]

# singleton instance
externalUrlManager = ExternalUrlManager()