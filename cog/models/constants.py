APPLICATION_LABEL = 'cog'

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
                       'Internet Chat',
                       'Wiki',
                       'Mailing List'
                     )

COMMUNICATION_CV = [ (x,x) for x in COMMUNICATION_TYPES ]


# list of tuples containing (role value, role display order)
LEAD_ORGANIZATIONAL_ROLES = (
                              ('Principal Investigator', 1),
                              ('Co-Investigator', 2),
                              ('Program Manager', 3),
                              ('Project Manager', 4),
                              ('Software Architect', 5),
                              ('Lead', 6),
                              ('Other Lead', 7),
                            )

# list of tuples containing (role value, role display order)
MEMBER_ORGANIZATIONAL_ROLES = (
                               ('Administrative Assistant', 1),
                               ('Data Manager', 2),
                               ('Outreach Coordinator', 3),
                               ('Researcher', 4),
                               ('Software Developer', 5),
                               ('Webmaster', 6),
                               ('Other Member', 7),
                              )

ORGANIZATIONAL_ROLE_CV = [ (x[0]," %s (Lead Role)" % x[0]) for x in LEAD_ORGANIZATIONAL_ROLES ] + [('','--------------')] + [ (x[0]," %s (Member Role)" % x[0]) for x in MEMBER_ORGANIZATIONAL_ROLES ]
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
                                 ('Review', 6),
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
FOOTER_LOGO = "cog/img/logo_1310_cogfootershrunk.PNG"


UPLOAD_DIR_PHOTOS = "photos/"
UPLOAD_DIR_LOGOS = "logos/"

# DEFAULT_IMAGES are located under static/cog/img/...
DEFAULT_IMAGES = { 'User':'cog/img/unknown.jpeg',
                   'Collaborator':'cog/img/unknown.jpeg',
                   'Organization':'cog/img/notfound.jpeg',
                   'FundingSource':'cog/img/notfound.jpeg'}

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
#MAX_UPLOADES_BYTES = 500000000

RESEARCH_KEYWORDS_MAX_CHARS = 60
RESEARCH_INTERESTS_MAX_CHARS = 1000

# signals
SIGNAL_OBJECT_CREATED = 'object_created'
SIGNAL_OBJECT_UPDATED = 'object_updated'
SIGNAL_OBJECT_DELETED = 'object_deleted'

DEFAULT_SEARCH_FACETS = { 'project':'Project',                         
                          'variable':'Variable' }
