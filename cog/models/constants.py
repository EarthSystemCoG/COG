APPLICATION_LABEL = 'cog'

# default template for project predefined pages, in the order they are displayed
# the first list item is the top-level tab, the others are sub-tabs
# IMPORTANT: the sub-tab URLs must start with the parent-tab URL (so that tabs can be properly selected)
PROJECT_PAGES = (
         [("Home", "")],
         [("About Us", "aboutus/"), ("Mission", "aboutus/mission/"), ("Vision", "aboutus/vision/"), ("Values", "aboutus/values/"),
          ("Partners", "aboutus/partners/"), ("Sponsors", "aboutus/sponsors/"), ("People", "aboutus/people/")], 
         #[("About Us", "aboutus/")],     
         # note that the bookmarks page is outside the project context, its URL is created later through a "reverse" lookup
         [("Bookmarks", "bookmarks/list/<project>/")],
         [("Code", "code/")],
         [("Trackers", "trackers/")],
         [("Support", "support/")],
         #[("Governance", "governance/"), ("Governance 1", "governance/g1/") ],
         [("Governance", "governance/")],
         #[("Roadmap", "roadmap/"), ("Roadmap 1", "roadmap/road1/"), ("Roadmap 2", "roadmap/road2/")],
         [("Roadmap", "roadmap/")],
         [("Contact Us", "contactus/")],            
         #("Administration", "admin/"),
        )

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
TYPE_POLICY = 'policy'
TYPE_ROADMAP = 'roadmap'

EXTERNAL_URL_TYPES = (       
    (TYPE_BLOG,'Blog'),
    (TYPE_CODE, 'Code'),
    (TYPE_HOMEPAGE,'Home Page'),
    (TYPE_REFERENCE,'Reference'),
    (TYPE_TRACKER, 'Tracker'),   
    (TYPE_POLICY, 'Policy'),
    (TYPE_ROADMAP, 'Roadmap'),      
)

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

# legacy media sub-directories of 'projects/'
SYSTEM_DOCS = 'system_docs'
SYSTEM_IMAGES = 'system_images'

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOADES_BYTES = 5242880