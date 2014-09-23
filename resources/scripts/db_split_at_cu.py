'''
Script to perform database setup at CoG-CU after 2.6.1 deployment (CoG sites split).

'''
import os
import sys
import cog
import shutil
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
noaaSite = Site.objects.get(domain='www.earthsystemcog.org')

# after DNS change:
#cuSite = Site.objects.get(domain='www.earthsystemcog.org')
#noaaSite = Site.objects.get(domain='cog-esgf.esrl.noaa.gov')
if cuSite != Site.objects.get_current():
    raise Exception("Running script for wrong site, exiting")

dryrun = True

# loop over projects
noaaProjects = ['HIWPP', 'CMDTF', 'CoupledNEMS', 'ESGF-ESRL',
                       'HIWPP_HurricaneNest', 'HIWPP_Hydrostatic', 'HIWPP_Internal',
                       'HIWPP_Management', 'HIWPP_NMME', 'HIWPP_NonHydrostatic', 'HIWPP_TestProgram',
                       ]

# delete NOAA projects
for project in Project.objects.all():
    
    if project.short_name in noaaProjects:
        deleteProject(project, dryrun=dryrun, rmdir=False) # do NOT delete directories (for now)
        

# loop over users
for user in User.objects.all():
       
    try:
        p = user.profile
    except ObjectDoesNotExist:
        p = UserProfile.objects.create(user=user)
        
    if user.profile.site == cuSite:
        
        print "Processing CU user: %s" % user
        
        # remove User password
        user.password = ''
        
        # update profile fields
        user.profile.type = 2 # (no CoG password)
        
        # transfer user affiliation from CU to NOAA
        print "\tUser affiliation changed from: %s to: %s" % (cuSite, noaaSite)
        user.profile.site = noaaSite
        
        # save changes
        if not dryrun:
            user.save()
            user.profile.save()
    
    else:
        pass
        #print 'Disregarding user=%s site=%s site_id=%s' % (user, user.profile.site, user.profile.site.id)