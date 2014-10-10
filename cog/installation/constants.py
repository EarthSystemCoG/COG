'''
Module containing shared constants for CoG installation.
'''
import os

SECTION_DEFAULT = 'DEFAULT'
SECTION_ESGF = 'ESGF'

ESG_CONFIG_DIR = os.getenv("esg_config_dir","/esg/config")
ESGF_PROPERTIES_FILE = '%s/esgf.properties' % ESG_CONFIG_DIR
ESGF_PASSWORD_FILE = '%s/.esg_pg_pass' % ESG_CONFIG_DIR
ESGF_IDP_WHITELIST = "%s/esgf_idp_static.xml" % ESG_CONFIG_DIR

# some default parameter values
DEFAULT_PROJECT_SHORT_NAME = 'TestProject'
