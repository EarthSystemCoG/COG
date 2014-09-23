'''
Script to perform database setup at CoG-NOAA after 2.6.1 deployment (CoG sites split).

'''
import os
import sys
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from cog.models import UserProfile

from cog.models import Project, deleteProject


# load CU, NOAA Sites

# before DNS change
cuSite = Site.objects.get(domain='cog-cu.colorado.edu')
noaaSite = Site.objects.get(domain='cog-esgf.esrl.noaa.gov')

# after DNS change:
#cuSite = Site.objects.get(domain='www.earthsystemcog.org')
#noaaSite = Site.objects.get(domain='cog-esgf.esrl.noaa.gov')
if noaaSite != Site.objects.get_current():
    raise Exception("Running script for wrong site, exiting")

dryrun = False

# loop over projects
noaaProjects = ['HIWPP', 'CMDTF', 'CoupledNEMS', 'ESGF-ESRL',
                'HIWPP_HurricaneNest', 'HIWPP_Hydrostatic', 'HIWPP_Internal',
                'HIWPP_Management', 'HIWPP_NMME', 'HIWPP_NonHydrostatic', 'HIWPP_TestProgram',
               ]

# delete non-NOAA projects
for project in Project.objects.all():
    
    if not project.short_name in noaaProjects:
        deleteProject(project, dryrun=dryrun, rmdir=True) # remove media directories