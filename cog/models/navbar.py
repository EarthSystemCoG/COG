''' 
Module containing configuration for upper navigation bar, 
i.e. for the project pre-defined pages.
'''

from external_url_conf import EXTERNAL_URL_TYPES, externalUrlManager
from folder_conf import folderManager

# dictionary containing (page key, page URL)
TABS = { "ABOUTUS":"aboutus", "MISSION":"mission", 
                              "VISION":"vision", 
                              "VALUES":"values", 
                              "IMPACTS":"impacts",
                              "HISTORY":"history", 
                              "PARTNERS":"partners", 
                              "SPONSORS":"sponsors", 
                              "PEOPLE":"people",
         "LOGISTICS":"logistics", "REGISTRATION":"registration",
                                  "LOCATION":"location",
                                  "LODGING":"lodging",
                                  "TRANSPORTATION":"transportation",
                                  "COMPUTING":"computing",
         "SOFTWARE":"software", "DOWNLOAD": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["DOWNLOAD"]).suburl, 
                                "ADMIN_GUIDE": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["ADMIN_GUIDE"]).suburl,
         "USERS":"users", "FAQ": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["FAQ"]).suburl,
                          "USER_GUIDE": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["USER_GUIDE"]).suburl,
                          "CODE_EXAMPLES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["CODE_EXAMPLE"]).suburl,
         "RESOURCES": folderManager.getFolderSubUrl('RESOURCES'), 'PUBLICATIONS': folderManager.getFolderSubUrl('PUBLICATIONS'),
                                                                  'PRESENTATIONS': folderManager.getFolderSubUrl('PRESENTATIONS'),
                                                                  'NEWSLETTERS': folderManager.getFolderSubUrl('NEWSLETTERS'),
                                                                  'PROPOSALS': folderManager.getFolderSubUrl('PROPOSALS'),
                                                                  'FIGURES': folderManager.getFolderSubUrl('FIGURES'),
                                                                  'TESTCASES': folderManager.getFolderSubUrl('TESTCASES'),
                                                                  'EVALUATIONS': folderManager.getFolderSubUrl('EVALUATIONS'),
         "DEVELOPERS":"developers", "REPOSITORIES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["REPOSITORY"]).suburl,
                                    "TRACKERS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["TRACKER"]).suburl,
                                    "DEVELOPER_GUIDE": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["DEVELOPER_GUIDE"]).suburl,
                                    "DESIGN_DOCS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["DESIGN_DOCUMENT"]).suburl,
                                    "TESTING": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["TESTING"]).suburl,
                                    "USECASES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["USECASE"]).suburl,
                                    "CHECKLIST": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["CHECKLIST"]).suburl,
         "PLANS":"plans", "ROADMAPS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["ROADMAPS"]).suburl,
                          "RELEASE_SCHEDULES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["RELEASE_SCHEDULE"]).suburl,
         "GOVERNANCE":"governance", "BODIES":"bodies",
                                    "ROLES":"roles", 
                                    "COMMUNICATION":"communication", 
                                    "PROCESSES":"processes", 
                                    "POLICIES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["POLICY"]).suburl,
                                    "MINUTES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["MINUTE"]).suburl,
                                    "METRICS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["METRIC"]).suburl,
         "CONTACTUS":"contactus"}

# list of pre-defined project pages
# RULES FOR TAB HIERARCHY
# o tab and subtab URLs must be of the form: 'projects/<project_short_name_lower>/<tab_label>/' where tab_label is unique
# o the selected sub-tab is found by matching the request path to the PROJECT_PAGES urls
# o the selected tab will be the one in position '0' in the list containing the selected sub-tab
# o everything after the third '/' is disregarded in computing the high-lighted tab and sub-tab
# o the tab/sub-tab URLs can be arbitrary except containing a '/'
PROJECT_PAGES = (
         [("Home", "")],
         [("About Us", "%s/" % TABS["ABOUTUS"]), ("Mission", "%s/" % TABS["MISSION"]), 
                                                 ("Vision", "%s/" % TABS["VISION"]), 
                                                 ("Values", "%s/" % TABS["VALUES"]),
                                                 ("Impacts", "%s/" % TABS["IMPACTS"]), 
                                                 ("History", "%s/" % TABS["HISTORY"]),
                                                 ("Partners", "%s/" % TABS["PARTNERS"]), 
                                                 ("Sponsors", "%s/" % TABS["SPONSORS"]), 
                                                 ("People", "%s/" % TABS["PEOPLE"])],   
        [("Agenda / Logistics", "%s/" % TABS["LOGISTICS"]), ("Registration", "%s/" % TABS["REGISTRATION"]), 
                                                   ("Location", "%s/" % TABS["LOCATION"]), 
                                                   ("Lodging", "%s/" % TABS["LODGING"]),
                                                   ("Transportation", "%s/" % TABS["TRANSPORTATION"]), 
                                                   ("Computing", "%s/" % TABS["COMPUTING"]), ],
         [("Software", "%s/" % TABS["SOFTWARE"]), ("Download / Releases", "%s/" % TABS["DOWNLOAD"]), 
                                                  ("Installer's / Administrator's Guide", "%s/" % TABS["ADMIN_GUIDE"])],
         [("Users", "%s/" % TABS["USERS"]), ("FAQ", "%s/" % TABS["FAQ"]), 
                                            ("User's Guide", "%s/" % TABS["USER_GUIDE"]), 
                                            ("Code Examples", "%s/" % TABS["CODE_EXAMPLES"]),],
         [("Developers", "%s/" % TABS["DEVELOPERS"]), ("Repositories", "%s/" % TABS["REPOSITORIES"]), 
                                                      ("Trackers", "%s/" % TABS["TRACKERS"]), 
                                                      ("Developer\'s Guide", "%s/" % TABS["DEVELOPER_GUIDE"]), 
                                                      ("Design Documents", "%s/" % TABS["DESIGN_DOCS"]), 
                                                      ("Testing", "%s/" % TABS["TESTING"]), 
                                                      ("Use Cases", "%s/" % TABS["USECASES"]), 
                                                      ("Checklist", "%s/" % TABS["CHECKLIST"]), ],
         [("Plans", "%s/" % TABS["PLANS"]), ("Roadmaps", "%s/" % TABS["ROADMAPS"]), 
                                            ("Release Schedules", "%s/" % TABS["RELEASE_SCHEDULES"])],
         [("Governance", "%s/" % TABS["GOVERNANCE"]), ("Bodies", "%s/" % TABS["BODIES"]), 
                                                      ("Roles", "%s/" % TABS["ROLES"]), 
                                                      ("Communications", "%s/" % TABS["COMMUNICATION"]),  
                                                      ("Processes", "%s/" % TABS["PROCESSES"]), 
                                                      ("Policies", "%s/" % TABS["POLICIES"]),
                                                      ("Minutes", "%s/" % TABS["MINUTES"]),
                                                      ("Metrics", "%s/" % TABS["METRICS"]), ],
         # Note: the tab names do not necessarily match the resource names
         [('Resources', "%s/" % TABS["RESOURCES"]), ('Publications', "%s/" % TABS["PUBLICATIONS"]),
                                                    ('Presentations', "%s/" % TABS["PRESENTATIONS"]),
                                                    ('Newsletters', "%s/" % TABS["NEWSLETTERS"]),
                                                    ('Proposals', "%s/" % TABS["PROPOSALS"]),
                                                    ('Figures', "%s/" % TABS["FIGURES"]),
                                                    ('Test Cases', "%s/" % TABS["TESTCASES"]),
                                                    ('Evaluations', "%s/" % TABS["EVALUATIONS"])],
         [("Contact Us", "%s/" % TABS["CONTACTUS"])],            
        )

# dictionary that maps tab suburls to tab labels
# "aboutus" --> "About Us"
TAB_LABELS = {}
for pages in PROJECT_PAGES:
    for page in pages:
        # remove trailing '/' from key
        TAB_LABELS[page[1][0:len(page[1])-1]] = page[0]
        
# labels of tabs that are enabled by default (i.e. at project creation)
DEFAULT_TABS = [ "Home", TAB_LABELS["aboutus"], TAB_LABELS["resources"], TAB_LABELS["contactus"] ]

# Navigational map: tab --> [suntabs]
# {
#  '': [], 
#  'support/': [], 
#  'governance/': [], 
# 'trackers/': [], 
# 'bookmarks/list/<project>/': [], 
# 'roadmap/': [], 
# 'contactus/': [], 
# 'aboutus/': ['aboutus/mission/', 'aboutus/vision/', 'aboutus/values/', 'aboutus/partners/', 'aboutus/sponsors/', 'aboutus/people/'], 
#'code/': []
# }
NAVMAP = {}
# Inverse navigational map: subtab --> tab
# { 
#   '': '', 
#   'aboutus/people/': 'aboutus/', 
#   'aboutus/vision/': 'aboutus/', 
#   'aboutus/partners/': 'aboutus/', 'governance/': 'governance/', 'aboutus/mission/': 'aboutus/', 'bookmarks/list/<project>/': 'bookmarks/list/<project>/', 'contactus/': 'contactus/', 'trackers/': 'trackers/', 'aboutus/values/': 'aboutus/', 'aboutus/sponsors/': 'aboutus/', 'roadmap/': 'roadmap/', 'support/': 'support/', 'aboutus/': 'aboutus/', 
#   'code/': 'code/'
# }
INVNAVMAP = {}
for tabs in PROJECT_PAGES:  
    taburl = tabs[0][1] 
    NAVMAP[ taburl ] = []
    INVNAVMAP[ taburl ] = taburl
    if len(tabs)>1:
        for ppage in tabs[1:]:
            subtaburl = ppage[1]
            NAVMAP[ taburl ].append( subtaburl )
            INVNAVMAP[ subtaburl ] = taburl