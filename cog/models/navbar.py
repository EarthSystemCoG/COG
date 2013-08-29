''' 
Module containing configuration for upper navigation bar, 
i.e. for the project pre-defined pages.
'''

from external_url_page import EXTERNAL_URL_PAGE_MAP

# dictionary containing (page key, page URL)
TABS = { "ABOUTUS":"aboutus", "MISSION":"mission", 
                              "VISION":"vision", 
                              "VALUES":"values", 
                              "HISTORY":"history", 
                              "PARTNERS":"partners", 
                              "SPONSORS":"sponsors", 
                              "PEOPLE":"people",
         "SOFTWARE":"software", "DOWNLOAD":EXTERNAL_URL_PAGE_MAP["download"].suburl, 
                                "ADMIN_GUIDE":EXTERNAL_URL_PAGE_MAP["admin_guide"].suburl,
         "USERS":"users", "FAQ":EXTERNAL_URL_PAGE_MAP["faq"].suburl, 
                          "USER_GUIDE":EXTERNAL_URL_PAGE_MAP["user_guide"].suburl, 
                          "CODE_EXAMPLES":EXTERNAL_URL_PAGE_MAP["code_examples"].suburl,
         "BOOKMARKS":"bookmarks",
         "DEVELOPERS":"developers", "REPOSITORIES":EXTERNAL_URL_PAGE_MAP["repositories"].suburl, 
                                    "TRACKERS":EXTERNAL_URL_PAGE_MAP["trackers"].suburl, 
                                    "DEVELOPER_GUIDE":EXTERNAL_URL_PAGE_MAP["developer_guide"].suburl, 
                                    "DESIGN_DOCS":EXTERNAL_URL_PAGE_MAP["design_docs"].suburl, 
                                    "TESTING":EXTERNAL_URL_PAGE_MAP["testing"].suburl, 
                                    "USECASES":EXTERNAL_URL_PAGE_MAP["usecases"].suburl, 
                                    "CHECKLIST":EXTERNAL_URL_PAGE_MAP["checklist"].suburl,
         "PLANS":"plans", "ROADMAP":"roadmap", 
                          "RELEASE_SCHEDULES":EXTERNAL_URL_PAGE_MAP["release_schedules"].suburl,
         "GOVERNANCE":"governance", "BODIES":"bodies",
                                    "ROLES":"roles", 
                                    "COMMUNICATION":"communication", 
                                    "PROCESSES":"processes", 
                                    "POLICIES":"policies",
                                    "MINUTES":EXTERNAL_URL_PAGE_MAP["minutes"].suburl,
                                    "METRICS":EXTERNAL_URL_PAGE_MAP["metrics"].suburl,
         "GETINVOLVED":"getinvolved", 
         "SUPPORT":"support",
         "CONTACTUS":"contactus"}

# list of pre-defined project pages
# RULES FOR TAB HIERARCHY
# o tab and subtab URLs must be of the form: 'projects/<project_short_name_lower>/<tab_label>/' whwre tab_label is unique
# o the selected sub-tab is found by matching the request path to the PROJECT_PAGES urls
# o the selected tab will be the one in position '0' in the list containing the selected sub-tab
# o everything after the third '/' is disregarded in computing the high-lighted tab and sub-tab
# o the tab/sub-tab URLs can be arbitrary except containing a '/'
PROJECT_PAGES = (
         [("Home", "")],
         [("About Us", "%s/" % TABS["ABOUTUS"]), ("Mission", "%s/" % TABS["MISSION"]), 
                                                 ("Vision", "%s/" % TABS["VISION"]), 
                                                 ("Values", "%s/" % TABS["VALUES"]),
                                                 ("History", "%s/" % TABS["HISTORY"]), 
                                                 ("Partners", "%s/" % TABS["PARTNERS"]), 
                                                 ("Sponsors", "%s/" % TABS["SPONSORS"]), 
                                                 ("People", "%s/" % TABS["PEOPLE"])],   
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
         [("Plans", "%s/" % TABS["PLANS"]), ("Roadmap", "%s/" % TABS["ROADMAP"]), 
                                            ("Release Schedules", "%s/" % TABS["RELEASE_SCHEDULES"])],
         [("Governance", "%s/" % TABS["GOVERNANCE"]), ("Bodies", "%s/" % TABS["BODIES"]), 
                                                      ("Roles", "%s/" % TABS["ROLES"]), 
                                                      ("Communication", "%s/" % TABS["COMMUNICATION"]),  
                                                      ("Processes", "%s/" % TABS["PROCESSES"]), 
                                                      ("Policies", "%s/" % TABS["POLICIES"]),
                                                      ("Minutes", "%s/" % TABS["MINUTES"]),
                                                      ("Metrics", "%s/" % TABS["METRICS"]), ],
         [("Bookmarks", "%s/" % TABS["BOOKMARKS"])],
         [("Get Involved", "%s/" % TABS["GETINVOLVED"])],
         [("Support", "%s/" % TABS["SUPPORT"])],
         [("Contact Us", "%s/" % TABS["CONTACTUS"])],            
        )

# dictionary that maps tab key to tab label
# "aboutus" --> "About Us"
TAB_LABELS = {}
for pages in PROJECT_PAGES:
    for page in pages:
        # remove trailing '/' from key
        TAB_LABELS[page[1][0:len(page[1])-1]] = page[0]

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