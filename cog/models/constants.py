APPLICATION_LABEL = 'cog'

# dictionary containing (page key, page url)
TABS = { "ABOUTUS":"aboutus", "MISSION":"mission", "VISION":"vision", "VALUES":"values", "HISTORY":"history", "PARTNERS":"partners", "SPONSORS":"sponsors", "PEOPLE":"people",
         "SOFTWARE":"software", "DOWNLOAD":"download", "ADMIN_GUIDE":"admin_guide",
         "USERS":"users", "FAQ":"faq", "USER_GUIDE":"user_guide", "CODE_EXAMPLES":"code_examples",
         "BOOKMARKS":"bookmarks",
         "DEVELOPMENT":"development", "CODE":"code", "TRACKERS":"trackers", "USECASES":"usecases",
         "ROADMAP":"roadmap",
         "GOVERNANCE":"governance","BODIES":"bodies","ROLES":"roles", "COMMUNICATION":"communication", "PROCESSES":"processes", "POLICIES":"policies",
         "GETINVOLVED":"getinvolved", 
         "SUPPORT":"support",
         "CONTACTUS":"contactus"}

#
# RULES FOR TAB HIERARCHY
# o tab and subtab URLs must be of the form: 'projects/<project_short_name_lower>/<tab_label>/' whwre tab_label is unique
# o the selected sub-tab is found by matching the request path to the PROJECT_PAGES urls
# o the selected tab will be the one in position '0' in the list containing the selected sub-tab
# o everything after the third '/' is disregarded in computing the high-lighted tab and sub-tab
# o the tab/sub-tab URLs can be arbitrary except containing a '/'
PROJECT_PAGES = (
         [("Home", "")],
         [("About Us", "%s/" % TABS["ABOUTUS"]), ("Mission", "%s/" % TABS["MISSION"]), ("Vision", "%s/" % TABS["VISION"]), ("Values", "%s/" % TABS["VALUES"]),
          ("History", "%s/" % TABS["HISTORY"]), ("Partners", "%s/" % TABS["PARTNERS"]), ("Sponsors", "%s/" % TABS["SPONSORS"]), ("People", "%s/" % TABS["PEOPLE"])],   
         [("Software", "%s/" % TABS["SOFTWARE"]), ("Download / Releases", "%s/" % TABS["DOWNLOAD"]), ("Installer's / Administrator's Guide", "%s/" % TABS["ADMIN_GUIDE"])],
         [("Users", "%s/" % TABS["USERS"]), ("FAQ", "%s/" % TABS["FAQ"]), ("User's Guide", "%s/" % TABS["USER_GUIDE"]), ("Code Examples", "%s/" % TABS["CODE_EXAMPLES"]),],
         [("Development", "%s/" % TABS["DEVELOPMENT"]), ("Code", "%s/" % TABS["CODE"]), ("Trackers", "%s/" % TABS["TRACKERS"]), ("Use Cases", "%s/" % TABS["USECASES"]), ],
         [("Roadmap", "%s/" % TABS["ROADMAP"])],
         [("Governance", "%s/" % TABS["GOVERNANCE"]), ("Bodies", "%s/" % TABS["BODIES"]), ("Roles", "%s/" % TABS["ROLES"]), 
                                                      ("Communication", "%s/" % TABS["COMMUNICATION"]),  ("Processes", "%s/" % TABS["PROCESSES"]), 
                                                      ("Policies", "%s/" % TABS["POLICIES"]) ],
         [("Bookmarks", "%s/" % TABS["BOOKMARKS"])],
         [("Get Involved", "%s/" % TABS["GETINVOLVED"])],
         [("Support", "%s/" % TABS["SUPPORT"])],
         [("Contact Us", "%s/" % TABS["CONTACTUS"])],            
        )

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


PURPOSE_TYPES = (
                 'Overall Project Coordination',
                 'Steering Committee',
                 'Design',
                 'Design and Implementation Review',
                 'Task Prioritization',
                 'Requirements Identification',
                 'Strategic Direction',
                 'External Review',
                 'Implementation',
                 'Meeting Planning',
                 'Testing',
                 'Knowledge Transfer',
                 'Grant Writing',
                 'Other',
                )
PURPOSE_CV = [ (x,x) for x in PURPOSE_TYPES ]

COMMUNICATION_TYPES = (
                       'Telco',
                       'Face-to-face',
                       'Webinar',
                       'Video Conference',
                       'Internet chat',
                       'Wiki',
                       'Mailing list'
                     )
COMMUNICATION_CV = [ (x,x) for x in COMMUNICATION_TYPES ]


# list of tuples containing (role value, role display order)
LEAD_ORGANIZATIONAL_ROLES = (
                              ('Principal Investigator', 1),
                              ('Co-Investigator', 2),
                              ('Program Manager', 3),
                              ('Project Manager', 4),
                              ('Software Architect', 5)
                            )

# list of tuples containing (role value, role display order)
MEMBER_ORGANIZATIONAL_ROLES = (
                               ('Administrative Assistant', 1),
                               ('Data Manager', 2),
                               ('Outreach Coordinator', 3),
                               ('Researcher', 4),
                               ('Software Developer', 5),
                               ('Webmaster', 6),
                               ('Other', 7)
                              )

ORGANIZATIONAL_ROLE_CV = [ (x[0]," %s (Lead Role)" % x[0]) for x in LEAD_ORGANIZATIONAL_ROLES ] + [ (x[0]," %s (Member Role)" % x[0]) for x in MEMBER_ORGANIZATIONAL_ROLES ]
# create and merge a combined dictionary of organizational roles
LEAD_ORGANIZATIONAL_ROLES_DICT = dict(LEAD_ORGANIZATIONAL_ROLES)
MEMBER_ORGANIZATIONAL_ROLES_DICT = dict(MEMBER_ORGANIZATIONAL_ROLES)
ORGANIZATIONAL_ROLES_DICT = dict( LEAD_ORGANIZATIONAL_ROLES_DICT.items() + MEMBER_ORGANIZATIONAL_ROLES_DICT.items() )

ROLE_CATEGORY_LEAD = 'Lead'
ROLE_CATEGORY_MEMBER = 'Member'
ORGANIZATIONAL_ROLE_CATEGORIES = (ROLE_CATEGORY_LEAD, ROLE_CATEGORY_MEMBER)
ORGANIZATIONAL_ROLE_CATEGORIES_CV = [ (x,x) for x in ORGANIZATIONAL_ROLE_CATEGORIES ]

MANAGEMENT_BODY_CATEGORY_STRATEGIC = 'Strategic'
MANAGEMENT_BODY_CATEGORY_OPERATIONAL = 'Operational'
MANAGEMENT_BODY_CATEGORIES = (MANAGEMENT_BODY_CATEGORY_STRATEGIC, MANAGEMENT_BODY_CATEGORY_OPERATIONAL)
MANAGEMENT_BODY_CATEGORIES_CV = [ (x,x) for x in MANAGEMENT_BODY_CATEGORIES ]

# list of tuples containing (management body value, management body display order)
STRATEGIC_MANAGEMENT_BODIES = (
                               ('Strategic Direction', 1),
                               ('Advice or Guidance', 2),
                               ('Program Direction', 3),
                               ('Review', 4),
                              )

# list of tuples containing (role value, role display order)
OPERATIONAL_MANAGEMENT_BODIES = (
                                 ('Research', 1),
                                 ('Development', 2),
                                 ('Requirements Identification', 3),
                                 ('Task Prioritization', 4),
                                 ('Testing', 5),
                                 ('Web Review', 6),
                                 ('Meeting and Event Planning', 7),
                                 ('Administration', 8),
                                )

MANAGEMENT_BODY_CV = [ (x[0]," %s (Strategic)" % x[0]) for x in STRATEGIC_MANAGEMENT_BODIES ] + [ (x[0]," %s (Operational)" % x[0]) for x in OPERATIONAL_MANAGEMENT_BODIES ]
# create and merge a combined dictionary of management bodies
STRATEGIC_MANAGEMENT_BODY_DICT = dict(STRATEGIC_MANAGEMENT_BODIES)
OPERATIONAL_MANAGEMENT_BODY_DICT = dict(OPERATIONAL_MANAGEMENT_BODIES)
MANAGEMENT_BODY_DICT = dict( STRATEGIC_MANAGEMENT_BODY_DICT.items() + OPERATIONAL_MANAGEMENT_BODY_DICT.items() )

MEMBERSHIP_TYPES = ('Open','Closed','By Invitation')

MEMBERSHIP_CV = [ (x,x) for x in MEMBERSHIP_TYPES ]

TYPE_BLOG = 'blog'
TYPE_CODE = 'code'
TYPE_HOMEPAGE = 'homepage'
TYPE_REFERENCE = 'reference'
TYPE_TRACKER = 'tracker'
TYPE_USECASE = 'usecase'
TYPE_POLICY = 'policy'
TYPE_ROADMAP = 'roadmap'
TYPE_DOWNLOAD = 'download'
TYPE_ADMIN_GUIDE = 'admin_guide'
TYPE_USER_GUIDE = 'user_guide'
TYPE_FAQ = 'faq'
TYPE_CODE_EXAMPLES = 'code_examples'

EXTERNAL_URL_TYPES = (       
    (TYPE_BLOG,'Blog'),
    (TYPE_CODE, 'Code'),
    (TYPE_HOMEPAGE,'Home Page'),
    (TYPE_REFERENCE,'Reference'),
    (TYPE_TRACKER, 'Tracker'),   
    (TYPE_USECASE, 'Use Case'),
    (TYPE_POLICY, 'Policy'),
    (TYPE_ROADMAP, 'Roadmap'), 
    (TYPE_DOWNLOAD,'Download'),
    (TYPE_ADMIN_GUIDE,'Administrator\'s Guide'),    
    (TYPE_USER_GUIDE,'User\'s Guide'), 
    (TYPE_FAQ,'FAQ'), 
    (TYPE_CODE_EXAMPLES,'Code Examples'), 
)

EXTERNAL_URL_DICT = {}
for tuple in EXTERNAL_URL_TYPES:
    EXTERNAL_URL_DICT[tuple[0]] = tuple[1]

ROLE_ADMIN = 'admin'
ROLE_USER = 'user'
ROLES = [ROLE_ADMIN, ROLE_USER]

DOCUMENT_TYPE_ALL = 'All'
DOCUMENT_TYPE_IMAGE = 'Image'
DOCUMENT_TYPE_TEXT = 'Text'
DOCUMENT_TYPE_PRESENTATION = 'Presentation'
DOCUMENT_TYPE_PROGRAM = 'Program'

DOCUMENT_TYPES = { 
                   DOCUMENT_TYPE_IMAGE: ['.gif', '.png', 'jpg,', '.jpeg'],
                   DOCUMENT_TYPE_TEXT:  ['.txt', '.pdf', '.doc', '.docx'], 
                   DOCUMENT_TYPE_PRESENTATION: ['.ppt','.pptx','.key'],
                   DOCUMENT_TYPE_PROGRAM: ['.java', '.py', '.sh']
                 }


# path of default logo relative to MEDIA_ROOT
# use a location outside of "logos/" so that the default logo can
#DEFAULT_LOGO = "img/admin/logo_1109_cog.JPG"
DEFAULT_LOGO = "cog/img/cog_web_beta.png"
FOOTER_LOGO = "cog/img/logo_nsf_and_noaa.bmp"

UPLOAD_DIR_PHOTOS = "photos/"
UPLOAD_DIR_LOGOS = "logos/"

DEFAULT_IMAGES = { 'User':'/%s/unknown.jpeg' % UPLOAD_DIR_PHOTOS,
                   'Collaborator':'/%s/unknown.jpeg' % UPLOAD_DIR_PHOTOS,
                   'Organization':'/%s/notfound.jpeg' % UPLOAD_DIR_LOGOS,
                   'FundingSource':'/%s/notfound.jpeg' % UPLOAD_DIR_LOGOS }

# legacy media sub-directories of 'projects/'
SYSTEM_DOCS = 'system_docs'
SYSTEM_IMAGES = 'system_images'

# 1MB - 1048576
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 52428800
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOADES_BYTES = 52428800

RESEARCH_KEYWORDS_MAX_CHARS = 60
RESEARCH_INTERESTS_MAX_CHARS = 1000

# signals
SIGNAL_OBJECT_CREATED = 'object_created'
SIGNAL_OBJECT_UPDATED = 'object_updated'
SIGNAL_OBJECT_DELETED = 'object_deleted'