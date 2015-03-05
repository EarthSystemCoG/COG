''' 
Module containing configuration for upper navigation bar, 
i.e. for the project pre-defined pages.
'''

from external_url_conf import EXTERNAL_URL_TYPES, externalUrlManager

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
         "SOFTWARE":"software", "RELEASE_SCHEDULES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["RELEASE_SCHEDULE"]).suburl,
                                "DOWNLOAD": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["DOWNLOAD"]).suburl, 
                                "ADMIN_DOCS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["ADMIN_DOCS"]).suburl,
         "USERS":"users", "FAQ": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["FAQ"]).suburl,
                          "USER_DOCS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["USER_DOCS"]).suburl,
                          "CODE_EXAMPLES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["CODE_EXAMPLE"]).suburl,
         "RESOURCES": "resources", 
         "DEVELOPERS":"developers", "REPOSITORIES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["REPOSITORY"]).suburl,
                                    "TRACKERS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["TRACKER"]).suburl,
                                    "DEV_DOCS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["DEV_DOCS"]).suburl,
                                    "TESTING": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["TESTING"]).suburl,
                                    "USECASES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["USECASE"]).suburl,
                                    "CHECKLIST": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["CHECKLIST"]).suburl,
                                    "PRIORITIZATION": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["PRIORITIZATION"]).suburl,
         "ROADMAPS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["ROADMAPS"]).suburl,
         "GOVERNANCE":"governance", "BODIES":"bodies",
                                    "ROLES":"roles", 
                                    "COMMUNICATION":"communication", 
                                    "PROCESSES":"processes", 
                                    "POLICIES": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["POLICY"]).suburl,
                                    "METRICS": externalUrlManager.getConf(type=EXTERNAL_URL_TYPES["METRIC"]).suburl,
         "FORUM":"forum",
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
         [("Software", "%s/" % TABS["SOFTWARE"]), ("Release Schedules", "%s/" % TABS["RELEASE_SCHEDULES"]),
                                                  ("Download / Releases", "%s/" % TABS["DOWNLOAD"]), 
                                                  ("Install / Admin Docs", "%s/" % TABS["ADMIN_DOCS"])],
         [("Users", "%s/" % TABS["USERS"]), ("FAQ", "%s/" % TABS["FAQ"]), 
                                            ("User Docs", "%s/" % TABS["USER_DOCS"]), 
                                            ("Code Examples", "%s/" % TABS["CODE_EXAMPLES"]),],
         [("Developers", "%s/" % TABS["DEVELOPERS"]), ("Repositories", "%s/" % TABS["REPOSITORIES"]), 
                                                      ("Trackers", "%s/" % TABS["TRACKERS"]), 
                                                      ("Dev Docs", "%s/" % TABS["DEV_DOCS"]), 
                                                      ("Testing", "%s/" % TABS["TESTING"]), 
                                                      ("Use Cases", "%s/" % TABS["USECASES"]),
                                                      ("Checklists", "%s/" % TABS["CHECKLIST"]), 
                                                      ("Prioritization", "%s/" % TABS["PRIORITIZATION"]), ],
         [("Roadmaps", "%s/" % TABS["ROADMAPS"]),],
         [("Metrics", "%s/" % TABS["METRICS"]),],
         [("Governance", "%s/" % TABS["GOVERNANCE"]), ("Bodies", "%s/" % TABS["BODIES"]), 
                                                      ("Roles", "%s/" % TABS["ROLES"]), 
                                                      ("Communications", "%s/" % TABS["COMMUNICATION"]),  
                                                      ("Processes", "%s/" % TABS["PROCESSES"]), 
                                                      ("Policies", "%s/" % TABS["POLICIES"]), ],
         # Note: the tab names do not necessarily match the resource names
         [('Resources', "%s/" % TABS["RESOURCES"]),],
         [("Forum", "%s/" % TABS["FORUM"])], 
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

# Navigational map: tab --> [subtabs]
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
