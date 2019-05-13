import os
import logging
import re
from cog.utils import str2bool

rel = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

log = logging.getLogger(__name__)

''' 
SITE SPECIFIC CONFIGURATION
These parameters are read from file 'cog_settings.cfg' 
located in directory COG_CONFIG_DIR (or by default '/usr/local/cog/cog_config').
Each parameter has a default value.
'''

from cog.site_manager import siteManager
from cog.constants import SECTION_ESGF, SECTION_PID


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s: %(message)s',
            'style': '%',
        },
    },
    'handlers': {
        'console': {
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('COG_LOG_FILE', rel('cog.log')),
            'maxBytes': 100*pow(2,20),
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'search': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('SEARCH_LOG_FILE', rel('search.log')),
            'maxBytes': 100*pow(2,20),
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'cog': {
            'handlers': ['file'],
            'level': os.getenv('COG_LOG_LEVEL', 'INFO'),
        },
        'cog.models.search': {
            'handlers': ['search'],
            'level': os.getenv('SEARCH_LOG_LEVEL', 'DEBUG'),
        },
        'cog.views.views_search': {
            'handlers': ['search'],
            'level': os.getenv('SEARCH_LOG_LEVEL', 'DEBUG'),
        },
        '__wsgi__': {
            'handlers': ['file'],
            'level': os.getenv('COG_LOG_LEVEL', 'INFO'),
        },
    },
}


SITE_NAME = siteManager.get('SITE_NAME', default='Local CoG')
SITE_DOMAIN = siteManager.get('SITE_DOMAIN', default='localhost:8000')
TIME_ZONE = siteManager.get('TIME_ZONE', default='America/Denver')
COG_MAILING_LIST = siteManager.get('COG_MAILING_LIST', default='cog_info@list.woc.noaa.gov')
SECRET_KEY = siteManager.get('SECRET_KEY', default='ds4sjjj(76K=={%$HHH1@#b:l;')
# for SQLLite back-end
DATABASE_PATH = siteManager.get('DATABASE_PATH', default="%s/django.data" % siteManager.cog_config_dir)
# for postgres back-end
DATABASE_NAME = siteManager.get('DATABASE_NAME', default='cogdb')
DATABASE_USER = siteManager.get('DATABASE_USER')
DATABASE_PASSWORD = siteManager.get('DATABASE_PASSWORD')
DATABASE_HOST = siteManager.get('DATABASE_HOST', default='localhost')
DATABASE_PORT = siteManager.get('DATABASE_PORT', default=5432)
MY_PROJECTS_REFRESH_SECONDS = int(siteManager.get('MY_PROJECTS_REFRESH_SECONDS', default=3600))  # one hour
PWD_EXPIRATION_DAYS = int(siteManager.get('PWD_EXPIRATION_DAYS', default=0))  # 0: no expiration
IDP_REDIRECT = siteManager.get('IDP_REDIRECT', default=None)
VISUS_SITE = siteManager.get('VISUS_SITE', default=None)
HOME_PROJECT = siteManager.get('HOME_PROJECT', default='cog')
MEDIA_ROOT = siteManager.get('MEDIA_ROOT', default="%s/site_media" % siteManager.cog_config_dir)
DEFAULT_SEARCH_URL = siteManager.get('DEFAULT_SEARCH_URL', default='http://hydra.fsl.noaa.gov/esg-search/search/')
DJANGO_DATABASE = siteManager.get('DJANGO_DATABASE', default='sqllite3')
if siteManager.get('DEBUG', default='False').lower() == 'true':
    DEBUG = True
else:
    DEBUG = False
ALLOWED_HOSTS = siteManager.get('ALLOWED_HOSTS', default=SITE_DOMAIN).split(",")
log.debug('Using DEBUG=%s ALLOWED_HOSTS=%s' % (DEBUG, ALLOWED_HOSTS))
IDP_WHITELIST = siteManager.get('IDP_WHITELIST', default=None)
log.debug('Using IdP whitelist(s): %s' % IDP_WHITELIST)
KNOWN_PROVIDERS = siteManager.get('KNOWN_PROVIDERS', default=None)
log.debug('Using list of known Identity Providers: %s' % KNOWN_PROVIDERS)
PEER_NODES = siteManager.get('PEER_NODES', default=None)
USE_CAPTCHA = str2bool(siteManager.get('USE_CAPTCHA', default='True'))
log.debug('Using list of ESGF/CoG peer nodes from: %s' % PEER_NODES)
# DEVELOPMENT/PRODUCTION server switch
PRODUCTION_SERVER = str2bool(siteManager.get('PRODUCTION_SERVER', default='False'))
log.debug('Production server flag=%s' % PRODUCTION_SERVER)

WPS_ENDPOINT = siteManager.get('WPS_ENDPOINT', default=None);
# Fields that will be added to the query string
WPS_FIELDS = siteManager.get('WPS_FIELDS', default='index_node').split(',');
WPS_DATACART = str2bool(siteManager.get('WPS_DATACART', default='False'))
log.debug('WPS endpoint: %s, datacart enabled: %s, fields: %s' % (WPS_ENDPOINT, WPS_DATACART, ','.join(WPS_FIELDS)))

# FIXME
# ESGF specific settings
ESGF_CONFIG = siteManager.isEsgfEnabled()
if ESGF_CONFIG:
    ESGF_HOSTNAME = siteManager.get('ESGF_HOSTNAME', section=SECTION_ESGF, default='')
    ESGF_DBURL = siteManager.get('ESGF_DBURL', section=SECTION_ESGF)
    ESGF_VERSION = siteManager.get('ESGF_VERSION', section=SECTION_ESGF)
# FIXME

# PID specific settings
PID_CONFIG = siteManager.isPidEnabled()
if PID_CONFIG:
    PID_PREFIX = siteManager.get('PID_PREFIX', section=SECTION_PID, default='21.14101')
    PID_MESSAGING_SERVICE_EXCHANGE = siteManager.get('PID_EXCHANGE', section=SECTION_PID, default='esgffed-exchange')
    PID_CREDENTIALS = siteManager.get('PID_CREDENTIALS', section=SECTION_PID, default=None).split('\n')

#====================== standard django settings.py ======================


# IMPORTANT: this setting must be set to True if using COG behind a proxy server,
# otherwise redirects won't work properly
USE_X_FORWARDED_HOST = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    # SQLite database
    'sqllite3': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2','postgresql','mysql','sqlite3' or 'oracle'.
        'NAME':   DATABASE_PATH,
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    # Postgres
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD,              # Not used with sqlite3.
        'HOST': DATABASE_HOST,                      # Defaults to 'localhost'
        'PORT': DATABASE_PORT,                      # Set to empty string for default. Not used with sqlite3.
    }

}

DATABASES['default'] = DATABASES[DJANGO_DATABASE]

logging.info('>>> Using Django database=%s' % DJANGO_DATABASE)
if DJANGO_DATABASE == 'sqllite3':
    logging.info("Database path=%s" % DATABASE_PATH)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Denver'
# use the system time zone, wherever the application is installed
#TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# current site identifier - always first site in database
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = rel('site_media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = 'http://localhost:8000/site_media/'
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/static/'
STATIC_ROOT = rel('static/')


# absolute path to root directory containing projects data
DATA_ROOT = os.path.join(MEDIA_ROOT, "data/")

# custom template, media and configuration directories
MYTEMPLATES = os.path.join(siteManager.cog_config_dir, 'mytemplates')
MYMEDIA = os.path.join(siteManager.cog_config_dir, 'mymedia')

# project-specific configuration directories
# must be writable by web server
PROJECT_CONFIG_DIR = os.path.join(MEDIA_ROOT, 'config')

log.debug('Loading custom templates from directories: %s, %s' % (MYTEMPLATES, MYMEDIA))

# Make this unique, and don't share it with anybody.
#SECRET_KEY = 'yb@$-bub$i_mrxqe5it)v%p=^(f-h&x3%uy040x))19g^iha&#'

# new TEMPLATES settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                 MYTEMPLATES,
                 rel('templates/'),
                 rel('static/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'cog.context_processors.cog_settings',
            ],
            'debug': DEBUG,
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cog.middleware.init_middleware.InitMiddleware',
    'cog.middleware.login_middleware.LoginMiddleware',
    'cog.middleware.session_middleware.SessionMiddleware',
    #'cog.middleware.password_middleware.PasswordMiddleware'
    #'django.contrib.sites.middleware.CurrentSiteMiddleware' # django 1.7
    #'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

#ROOT_URLCONF = 'COG.urls'
ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django_openid_auth',
    'grappelli',
    'filebrowser',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django_comments',
    'django.contrib.staticfiles',
    'captcha',
    'layouts',
    'cog.apps.CogConfig',
    'cog.templatetags',
)

MIGRATION_MODULES = { 'django_openid_auth': 'cog.db_migrations.django_openid_auth' }

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Default is X_FRAME_OPTIONS='SAMEORIGIN'
# Using X_FRAME_OPTIONS = DENY breaks the CKEditor file uploader.
#X_FRAME_OPTIONS = 'DENY'

# login page URL (default: '/accounts/login')
LOGIN_URL = '/login/'

# OpenID login page
#LOGIN_URL = '/openid/login/'

# page to redirect after successful authentication, if 'next' parameter is not provided
#LOGIN_REDIRECT_URL='/cog/' # COG projects index
LOGIN_REDIRECT_URL = '/'  # welcome page

# Custom user profile
AUTH_PROFILE_MODULE = "cog.UserProfile"


# HTTPS support: can only send cookies via SSL connections
if PRODUCTION_SERVER:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    #SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSS styles
#COLOR_DARK_TEAL = "#358C92"
#COLOR_LIGHT_TEAL = "#B9E0E3"

#COLOR_DARK_YELLOW = "#FAC2A4";
#COLOR_LIGHT_YELLOW = "#FCE79F";

#COLOR_DARK_GRAY = "#666666";

# FIXME: necessary for openid-auth since django 1.6.5 otherwise session is not serialized correctly
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# default size limit of files uploaded by users
MAX_UPLOAD_SIZE = 52428800

#=== django filebrowser settings =========================

# Filebrowser directory relative to MEDIA_ROOT (IMPORTANT: must have trailing slash)
FILEBROWSER_DIRECTORY = "projects/"

# versions generated when browsing images
FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'thumbnail': {'verbose_name': 'Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    #'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
    #'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
    #'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
    #'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
}

# versions selectable through admin interface
FILEBROWSER_ADMIN_VERSIONS = ['thumbnail']

# absolute path to directory containing project specific media
PROJECTS_ROOT = os.path.join(MEDIA_ROOT, FILEBROWSER_DIRECTORY)

#=== django_openid_auth settings =========================

# create user account after first openid authentication
OPENID_CREATE_USERS = True

# do / do NOT keep updating the user profile from the IdP
OPENID_UPDATE_DETAILS_FROM_SREG = True

# list of allowed hosts to redirect to after successful openid login
# this is because django-openid-auth does not allow redirection to full URLs by default,
# unless the host is specifically enabled
ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS = [re.sub(':\d+','', SITE_DOMAIN) ]

#===== django-simpla-captcha =========

#CAPTCHA_LETTER_ROTATION = None
CAPTCHA_BACKGROUND_COLOR = '#FAC24A' # matches CoG dark yellow
#CAPTCHA_FOREGROUND_COLOR = "#666666" # matches CoG dark gray
CAPTCHA_IMAGE_SIZE = (100, 40)
#CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'

#==== Quality Control Flags references ==================================

QCFLAGS_URLS = { 'obs4mips_indicators': 'https://www.earthsystemcog.org/projects/obs4mips/data-indicators' }
