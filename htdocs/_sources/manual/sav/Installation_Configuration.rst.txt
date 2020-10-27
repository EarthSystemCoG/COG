
Installation Configuration
==========================

Configuration of CoG is handled via the $COG_CONFIG_DIR/cog_settings.cfg
file. There are several environment variables that must be set and many
more that can be set if desired to modify the node configuration.

Values set in this file will not be overridden by future upgrades.

Updating the SITE_NAME
----------------------

If for any reason or of the current node needs to change, the command
below will need to be run (You do not have to do this for any other
variable in the cog_settings.cfg file.)

python manage.py init_site

Configuration Variables
-----------------------

.. csv-table::
   :header:  "Variable", "Meaning", "Example"
   :widths:  20, 20, 50
   :align:   left


   "SITE_NAME", "A short human readable name identifying this specific CoG instance", "SITE_NAME = LOCALHOST"
   "SITE_DOMAIN", "The node domain name and optional port number, without any protocol.", "SITE_DOMAIN = localhost:8000"   
   "TIME_ZONE", "The node specific time zone - see list of Django values for time zones", "TIME_ZONE=America/Denver"
   "SECRET_KEY", "The node specific key: an arbitrary string with lots of strange characters. A random string is 
   generated when CoG is first installed, but you may want to replace it with your own long sequence of random characters
   and keep it secret.","SECRET_KEY=yb@$-bub$i_mr34dda%p=^(f-h&dsdaudssduy040x))19g^iha&#1134df4"
   "COG_MAILING_LIST", 	"Low-traffic CoG mailing list used to announce downtimes and system upgrades.",  "COG_MAILING_LIST=cog_info@list.woc.noaa.gov"
   "DJANGO_DATABASE", "The specific database back-end database. 'postgres' or 'sqllite3' are the only two options.", "DJANGO_DATABASE = sqllite3"
   "DATABASE_PATH", "Location of the database", "DATABASE_PATH = /Users/sylvia.murphy/COG/cog_config/django.data"
   "DATABASE_NAME", "Name of CoG postgres database (only needed if using Postgres database.)","DATABASE_NAME=cogdb"
   "DATABASE_USER", "Username to access the database (only needed if using Postgres).", "DATABASE_USER=None"
   "DATABASE_PASSWORD", "Password to access the database (only needed if using Postgres).", "DATABASE_PASSWORD=<db_password>"
   "DATABASE_PORT", "Port of database (only needed if using Postgres)", "DATABASE_PORT=5432"
   "HOME_PROJECT", "short name of the project that serves as the node home (i.e. where requests to '/' are redirected).", "HOME_PROJECT=TestProject"
   "MY_PROJECTS_REFRESH_SECONDS", "Time interval to check for updates of user project memberships. Do not make this too short. Units is seconds.", "MY_PROJECTS_REFRESH_SECONDS = 3600"
   "PASSWORD_EXPIRATION_DAYS", "Optional number of days after which password expire. 0 means passwords never expire.", "PASSWORD_EXPIRATION_DAYS=150"
   "IDP_REDIRECT", "Optional top-level URL to redirect user registration (no trailing '/'). Use only if the CoG installation has no associated ESGF node.", "IDP_REDIRECT="
   "MEDIA_ROOT", "Location of node-specific site_media directory (where all projects and users content is uploaded to)", "MEDIA_ROOT = /Users/sylvia.murphy/COG/cog_config/site_media"
   "DEFAULT_SEARCH_URL", "Default ESGF search service URL for projects that enable the data search", "DEFAULT_SEARCH_URL=http://esg-datanode.jpl.nasa.gov/esg-search/search/ [ESGF]"
   "ESGF_HOSTNAME", "ESGF Identity Provider hostname", "ESGF_HOSTNAME=hydra.fsl.noaa.gov"
   "ESGF_DBURL", "ESGF postgres database access string", "ESGF_DBURL=postgresql://:@localhost/esgcet"
   "IDP_WHITELIST", "White list of trusted ESGF identity providers", "IDP_WHITELIST = /esg/config/esgf_idp.xml, /esg/config/esgf_idp_static.xml"
   "EMAIL_SERVER", "Email server", "EMAIL_SERVER = smtp.gmail.com"
   "EMAIL_PORT", "Email port (leave blank if using the default)", "EMAIL_PORT = # Address that will show up as sending CoG emails"
   "EMAIL_SENDER", "Address that will show up as sending CoG emails", "EMAIL_SENDER = Earth System COG"
   "EMAIL_USERNAME", "Email server username", "EMAIL_USERNAME = <username>"
   "EMAIL_PASSWORD", "Email server password", "EMAIL_PASSWORD = <password>"
   "EMAIL_SECURITY", "Email server handshake startup instruction (use only if needed)", "EMAIL_SECURITY = STARTTLS"
   "DEBUG", "Always use False in production!!!", "DEBUG=False"
   "ALLOWED_HOSTS", 	"Coma separated list of node names, without port. Mandatory if DEBUG=False otherwise every request will result in HTTP Error 400", "ALLOWED_HOSTS = localhost"
   "KNOWN_PROVIDERS", "_", "KNOWN_PROVIDERS = /esg/config/esgf_known_providers.xml"
   "PRODUCTION_SERVER",  "It needs to be set to True only when using a server with SSL support, other wise login will", "PRODUCTION_SERVER = False"
   

   
  

 
