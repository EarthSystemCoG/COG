'''
Module containing shared constants for CoG installation.
'''
import os

COG_SECTION_DEFAULT = 'DEFAULT'
SECTION_DEFAULT = 'installer.properties'
SECTION_ESGF = 'ESGF'
SECTION_EMAIL = 'EMAIL'

ESG_CONFIG_DIR = os.getenv("esg_config_dir","/esg/config")
ESGF_PROPERTIES_FILE = '%s/esgf.properties' % ESG_CONFIG_DIR
ESGF_PASSWORD_FILE = '%s/.esg_pg_pass' % ESG_CONFIG_DIR
IDP_WHITELIST = "%s/esgf_idp.xml, %s/esgf_idp_static.xml" % (ESG_CONFIG_DIR, ESG_CONFIG_DIR)
ESGF_ROOTADMIN_PASSWORD_FILE = '%s/.esgf_pass' % ESG_CONFIG_DIR
ROOTADMIN_USERNAME = "rootAdmin"
DEFAULT_ROOTADMIN_PWD = "changeit"
ROOTADMIN_GROUP = "wheel"
ROOTADMIN_ROLE = "super"
KNOWN_PROVIDERS = "%s/esgf_known_providers.xml" % ESG_CONFIG_DIR
PEER_NODES = "%s/esgf_cogs.xml" % ESG_CONFIG_DIR

# some default parameter values
DEFAULT_PROJECT_SHORT_NAME = 'TestProject'
